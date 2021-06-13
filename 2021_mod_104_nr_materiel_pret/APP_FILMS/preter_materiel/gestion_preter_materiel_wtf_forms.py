"""
    Fichier : gestion_clients_wtf_forms.py
    Auteur : OM 2021.03.22
    Gestion des formulaires avec WTF
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Length
from wtforms.validators import Regexp


class FormWTFAjouterpretermateriel(FlaskForm):
    """
        Dans le formulaire "client_ajouter_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    preter_materiel_regexp = "^[a-zA-Z0-9_]+$"
    preter_materiel_wtf = StringField("Clavioter l'état ", validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                                   Regexp(preter_materiel_regexp,
                                                                          message="Pas de chiffres, de caractères "
                                                                                  "spéciaux, "
                                                                                  "d'espace à double, de double "
                                                                                  "apostrophe, de double trait union")
                                                                   ])

    submit = SubmitField("Enregistrer client")


class FormWTFUpdatepretermateriel(FlaskForm):
    """
        Dans le formulaire "client_update_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    preter_materiel_update_regexp = "^[a-zA-Z0-9_]+$"
    preter_materiel_update_wtf = StringField("Clavioter l'état ", validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                                          Regexp(preter_materiel_update_regexp,
                                                                                 message="Il n'y  pas de symbole dans un nom !")
                                                                          ])

    submit = SubmitField("Update clients")


class FormWTFDeleteclients(FlaskForm):
    """
        Dans le formulaire "client_delete_wtf.html"

        nom_client_delete_wtf : Champ qui reçoit la valeur du client, lecture seule. (readonly=true)
        submit_btn_del : Bouton d'effacement "DEFINITIF".
        submit_btn_conf_del : Bouton de confirmation pour effacer un "client".
        submit_btn_annuler : Bouton qui permet d'afficher la table "t_client".
    """
    nom_client_delete_wtf = StringField("Effacer ce client")
    submit_btn_del = SubmitField("Effacer client")
    submit_btn_conf_del = SubmitField("Etes-vous sur d'effacer ?")
    submit_btn_annuler = SubmitField("Annuler")
