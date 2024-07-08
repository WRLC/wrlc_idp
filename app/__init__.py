import os
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, hash_password, uia_username_mapper
from flask_saml2.utils import certificate_from_file, private_key_from_file
from app.models.user import User
from app.models.role import Role
from app.models.username_util import UsernameUtil
from app.models.institution import Institution
from config import Config
from app.extensions import db
from dotenv import load_dotenv
from datetime import datetime
from flask_mailman import Mail

load_dotenv()


def create_app(config_class=Config):
    app = Flask(__name__)  # Create the Flask app
    app.config.from_object(config_class)  # Load the configuration file

    db.init_app(app)  # Initialize the database

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role, None)
    app.security = Security(app, user_datastore, username_util_cls=UsernameUtil)
    app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = [
        {"username": {"mapper": uia_username_mapper, "case_insensitive": False}},
    ]

    # Setup Flask-SAML2
    app.config['SAML2_IDP'] = {  # Identity Provider configuration
        'autosubmit': True,
        'certificate': certificate_from_file(os.getenv("SAML2_IDP_CERTIFICATE")),
        'private_key': private_key_from_file(os.getenv("SAML2_IDP_PRIVATE_KEY")),
    }

    app.config['SAML2_SERVICE_PROVIDERS'] = [  # External Service Provider configuration
        {
            'CLASS': 'app.saml.models.flaskloginsphandler.FlaskLoginSPHandler',
            'OPTIONS': {
                'display_name': os.getenv('SAML2_SP_DISPLAY_NAME'),
                'entity_id': os.getenv('SAML2_SP_ENTITY_ID'),
                'acs_url': os.getenv('SAML2_SP_ACS_URL'),
                'certificate': certificate_from_file(os.getenv("SAML2_SP_CERTIFICATE")),
            }
        }
    ]

    # This processor is added to all emails
    @app.security.mail_context_processor
    def security_mail_processor():
        return dict(base_url=app.config['SERVER_NAME'])

    # Setup Flask-Mailman
    mail = Mail(app)  # Create the mail extension
    mail.init_app(app)  # Initialize the mail extension

    # Register blueprints here
    from app.idp import bp  # IdP blueprint
    app.register_blueprint(bp)

    from app.saml import samlbp  # SAML blueprint
    app.register_blueprint(samlbp, url_prefix='/saml/')

    with (app.app_context()):
        db.create_all()  # Create the database tables
        # Create admin role
        if not app.security.datastore.find_role(os.getenv("ADMIN_ROLE")):
            app.security.datastore.create_role(
                name=os.getenv("ADMIN_ROLE"),
                description=os.getenv("ADMIN_ROLE_DESCRIPTION")
            )
        db.session.commit()

        # Create user role
        if not app.security.datastore.find_role(os.getenv("USER_ROLE")):
            app.security.datastore.create_role(
                name=os.getenv("USER_ROLE"),
                description=os.getenv("USER_ROLE_DESCRIPTION")
            )

        # Create admin institution
        if db.session.execute(db.select(Institution).filter_by(code=os.getenv("ADMIN_INST_CODE"))).scalar() is None:
            institution = Institution(
                code=os.getenv("ADMIN_INST_CODE"),
                name=os.getenv("ADMIN_INST_NAME"),
                created=datetime.now()
            )
            db.session.add(institution)
            db.session.commit()

        # Create admin user
        if not app.security.datastore.find_user(username=os.getenv("ADMIN_USERNAME")):
            institution = db.session.execute(
                db.select(Institution).filter_by(code=os.getenv("ADMIN_INST_CODE"))
            ).scalar()
            app.security.datastore.create_user(
                email=os.getenv("ADMIN_EMAIL"),
                username=os.getenv("ADMIN_USERNAME"),
                password=hash_password(os.getenv("ADMIN_PASSWORD")),
                first_name=os.getenv("ADMIN_FIRST_NAME"),
                last_name=os.getenv("ADMIN_LAST_NAME"),
                institution=institution.id,
                roles=[
                    app.security.datastore.find_role(os.getenv("ADMIN_ROLE")),
                    app.security.datastore.find_role(os.getenv("USER_ROLE"))
                ],
                created=datetime.now()
            )
        db.session.commit()
    return app
