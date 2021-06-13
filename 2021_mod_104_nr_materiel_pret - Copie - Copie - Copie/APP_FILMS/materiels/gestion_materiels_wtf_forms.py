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


class FormWTFAjoutermateriels(FlaskForm):
    """
        Dans le formulaire "materiels_ajouter_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    nom_materiel_regexp = "^[a-zA-Z0-9_]+$"
    nom_materiel_wtf = StringField("Clavioter le matériel ", validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                                   Regexp(nom_materiel_regexp,
                                                                          message="Pas de chiffres, de caractères "
                                                                                  "spéciaux, "
                                                                                  "d'espace à double, de double "
                                                                                  "apostrophe, de double trait union")
                                                                   ])
    nom_numero_serie_regexp = "^[a-zA-Z0-9_]+$"
    nom_numero_serie_wtf = StringField("Clavioter le numéro de série ", validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                                         Regexp(nom_numero_serie_regexp,
                                                                                message="Vérifiez votre numéro de série")

                                                                         ])
    submit = SubmitField("Enregistrer matériel")


class FormWTFUpdatemateriel(FlaskForm):
    """
        Dans le formulaire "materiel_update_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    nom_materiel_update_regexp = "^[a-zA-Z0-9_]+$"
    nom_materiel_update_wtf = StringField("Clavioter le matériel ", validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                                          Regexp(nom_materiel_update_regexp,
                                                                                 message="Vous ne savez pas clavioter un matériel correctement")
                                                                          ])
    nom_numero_serie_update_regexp = "^[a-zA-Z0-9_]+$"
    nom_numero_serie_update_wtf = StringField("Clavioter le numéro de série ",
                                       validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                   Regexp(nom_numero_serie_update_regexp,
                                                          message="Vérifiez votre numéro de série")

                                                   ])
    submit = SubmitField("Update materiel")


class FormWTFDeletemateriel(FlaskForm):
    """
        Dans le formulaire "materiel_delete_wtf.html"

        nom_materiel_delete_wtf : Champ qui reçoit la valeur du matériel, lecture seule. (readonly=true)
        submit_btn_del : Bouton d'effacement "DEFINITIF".
        submit_btn_conf_del : Bouton de confirmation pour effacer un "materiel".
        submit_btn_annuler : Bouton qui permet d'afficher la table "t_materiel".
    """
    nom_materiel_delete_wtf = StringField("Effacer ce materiel")
    submit_btn_del = SubmitField("Effacer materiel")
    submit_btn_conf_del = SubmitField("Etes-vous sur d'effacer ?")
    submit_btn_annuler = SubmitField("Annuler")
