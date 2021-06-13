"""
    Fichier : gestion_materiels_crud.py
    Auteur : OM 2021.03.16
    Gestions des "routes" FLASK et des données pour les materiels.
"""
import sys

import pymysql
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from APP_FILMS import obj_mon_application
from APP_FILMS.database.connect_db_context_manager import MaBaseDeDonnee
from APP_FILMS.erreurs.exceptions import *
from APP_FILMS.erreurs.msg_erreurs import *
from APP_FILMS.materiels.gestion_materiels_wtf_forms import FormWTFAjoutermateriels
from APP_FILMS.materiels.gestion_materiels_wtf_forms import FormWTFDeletemateriel
from APP_FILMS.materiels.gestion_materiels_wtf_forms import FormWTFUpdatemateriel

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /materiels_afficher
    
    Test : ex : http://127.0.0.1:5005/materiels_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                Id_materiel_sel = 0 >> tous les materiels.
                Id_materiel_sel = "n" affiche le materiel dont l id est "n"
"""


@obj_mon_application.route("/materiels_afficher/<string:order_by>/<int:Id_materiel_sel>", methods=['GET', 'POST'])
def materiels_afficher(order_by, Id_materiel_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion materiels ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur Gestionmateriels {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                if order_by == "ASC" and Id_materiel_sel == 0:
                    strsql_materiels_afficher = """SELECT Id_materiel, materiel, numero_de_serie FROM t_materiel
                     ORDER BY Id_materiel ASC"""
                    mc_afficher.execute(strsql_materiels_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_materiel"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du materiel sélectionné avec un nom de variable
                    valeur_Id_materiel_selected_dictionnaire = {"value_Id_materiel_selected": Id_materiel_sel}
                    strsql_materiels_afficher = """SELECT Id_materiel, materiel, numero_de_serie FROM t_materiel 
                    WHERE Id_materiel = %(value_Id_materiel_selected)s"""

                    mc_afficher.execute(strsql_materiels_afficher, valeur_Id_materiel_selected_dictionnaire)
                else:
                    strsql_materiels_afficher = """SELECT Id_materiel, materiel, numero_de_serie     
                    FROM t_materiel ORDER BY Id_materiel DESC"""

                    mc_afficher.execute(strsql_materiels_afficher)

                data_materiels = mc_afficher.fetchall()

                print("data_materiels ", data_materiels, " Type : ", type(data_materiels))

                # Différencier les messages si la table est vide.
                if not data_materiels and Id_materiel_sel == 0:
                    flash("""La table "t_materiel" est vide. !!""", "warning")
                elif not data_materiels and Id_materiel_sel > 0:
                    # Si l'utilisateur change l'id_materiel dans l'URL et que le materiel n'existe pas,
                    flash(f"Le materiel demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_materiel" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données matériel affichés !!", "success")

        except Exception as erreur:
            print(f"RGG Erreur générale. materiels_afficher")
            # OM 2020.04.09 On dérive "Exception" par le "@obj_mon_application.errorhandler(404)"
            # fichier "run_mon_app.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            flash(f"RGG Exception {erreur} materiels_afficher", "danger")
            raise Exception(f"RGG Erreur générale. {erreur}")
            # raise MaBdErreurOperation(f"RGG Exception {msg_erreurs['ErreurNomBD']['message']} {erreur}")

    # Envoie la page "HTML" au serveur.
    return render_template("materiels/materiels_afficher.html", data=data_materiels)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /materiels_ajouter
    
    Test : ex : http://127.0.0.1:5005/materiels_ajouter
    
    Paramètres : sans
    
    But : Ajouter un materiel pour un film
    
    Remarque :  Dans le champ "name_materiel_html" du formulaire "materiels/materiels_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/materiels_ajouter", methods=['GET', 'POST'])
def materiels_ajouter_wtf():
    form = FormWTFAjoutermateriels()
    if request.method == "POST":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion materiels ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur Gestionmateriels {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            if form.validate_on_submit():
                name_materiel_wtf = form.nom_materiel_wtf.data
                name_numero_serie_wtf = form.nom_numero_serie_wtf.data

                name_materiel = name_materiel_wtf.lower()
                name_numero_serie = name_numero_serie_wtf.lower()
                valeurs_insertion_dictionnaire = {"value_numero_serie": name_numero_serie,
                                                  "value_materiel": name_materiel}
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                # INSERT INTO `t_materiel` (`Id_materiel`, `materiel`, `numero_de_serie`) VALUES (NULL, 'chier', '24');
                strsql_insert_materiel = """INSERT INTO t_materiel (Id_materiel,materiel, numero_de_serie) 
                VALUES (NULL,%(value_materiel)s,%(value_numero_serie)s)"""
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(strsql_insert_materiel, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('materiels_afficher', order_by='DESC', Id_materiel_sel=0))

        # ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except pymysql.err.IntegrityError as erreur_materiel_doublon:
            # Dérive "pymysql.err.IntegrityError" dans "MaBdErreurDoublon" fichier "erreurs/exceptions.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            code, msg = erreur_materiel_doublon.args

            flash(f"{error_codes.get(code, msg)} ", "warning")

        # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except (pymysql.err.OperationalError,
                pymysql.ProgrammingError,
                pymysql.InternalError,
                TypeError) as erreur_gest_genr_crud:
            code, msg = erreur_gest_genr_crud.args

            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Erreur dans Gestion materiels CRUD : {sys.exc_info()[0]} "
                  f"{erreur_gest_genr_crud.args[0]} , "
                  f"{erreur_gest_genr_crud}", "danger")

    return render_template("materiels/materiels_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /materiel_update
    
    Test : ex cliquer sur le menu "materiels" puis cliquer sur le bouton "EDIT" d'un "materiel"
    
    Paramètres : sans
    
    But : Editer(update) un materiel qui a été sélectionné dans le formulaire "materiels_afficher.html"
    
    Remarque :  Dans le champ "nom_materiel_update_wtf" du formulaire "materiels/materiel_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/materiel_update", methods=['GET', 'POST'])
def materiel_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_materiel"
    id_materiel_update = request.values['id_materiel_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdatemateriel()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "materiel_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            name_materiel_update = form_update.nom_materiel_update_wtf.data
            name_numero_serie_update = form_update.nom_numero_serie_update_wtf.data

            name_materiel_update = name_materiel_update.lower()
            name_numero_serie_update = name_numero_serie_update.lower()

            valeur_update_dictionnaire = {"value_Id_materiel": id_materiel_update,
                                          "value_name_materiel": name_materiel_update,
                                          "value_numero_serie": name_numero_serie_update}

            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            # UPDATE `t_materiel` SET `materiel` = 'clavier sans fil', `numero_de_serie` = '122123FDR' WHERE `t_materiel`.`Id_materiel` = 4;
            str_sql_update_materiel = """UPDATE t_materiel SET materiel = %(value_name_materiel)s, numero_de_serie = %(value_numero_serie)s WHERE t_materiel . Id_materiel = %(value_Id_materiel)s"""
            with MaBaseDeDonnee() as mconn_bd:
                mconn_bd.mabd_execute(str_sql_update_materiel, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_materiel_update"
            return redirect(url_for('materiels_afficher', order_by="ASC", Id_materiel_sel=id_materiel_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_materiel" et "materiel" de la "t_materiel"
            str_sql_Id_materiel = "SELECT Id_materiel, materiel, numero_de_serie FROM t_materiel WHERE Id_materiel = %(value_Id_materiel)s"
            valeur_select_dictionnaire = {"value_Id_materiel": id_materiel_update}
            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()
            mybd_curseur.execute(str_sql_Id_materiel, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom materiel" pour l'UPDATE
            data_materiel = mybd_curseur.fetchone()
            print(data_materiel)
            print("data_nom_materiel ", data_materiel, " type ", type(data_materiel), " materiel ",
                  data_materiel["materiel"])
            print("data_nom_numero_serie ", data_materiel, " type ", type(data_materiel), " numero_serie ",
                  data_materiel["numero_serie"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "materiel_update_wtf.html"
            form_update.nom_materiel_update_wtf.data = data_materiel["materiel"]
            form_update.nom_numero_serie_update_wtf.data = data_materiel["numero_de_serie"]

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans materiel_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
        flash(f"__KeyError dans numero_serie_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans materiel_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
        flash(f"Erreur dans numero_serie_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")
        flash(f"Erreur dans materiel_update_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")
        flash(f"__KeyError dans materiel_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("materiels/materiel_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /materiel_delete
    
    Test : ex. cliquer sur le menu "matériel" puis cliquer sur le bouton "DELETE" d'un "matériel"
    
    Paramètres : sans
    
    But : Effacer(delete) un materiel qui a été sélectionné dans le formulaire "materiels_afficher.html"
    
    Remarque :  Dans le champ "nom_materiel_delete_wtf" du formulaire "materiels/materiel_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@obj_mon_application.route("/materiel_delete", methods=['GET', 'POST'])
def materiel_delete_wtf():
    data_films_attribue_materiel_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_materiel"
    id_materiel_delete = request.values['id_materiel_btn_delete_html']

    # Objet formulaire pour effacer le materiel sélectionné.
    form_delete = FormWTFDeletemateriel()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("materiels_afficher", order_by="ASC", Id_materiel_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "materiels/materiel_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_materiel_delete = session['data_films_attribue_materiel_delete']
                print("data_films_attribue_materiel_delete ", data_films_attribue_materiel_delete)

                flash(f"Effacer le materiel de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer materiel" qui va irrémédiablement EFFACER le materiel
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_Id_materiel": id_materiel_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_preter_materiel = """DELETE FROM t_preter_materiel WHERE fk_materiel = %(value_Id_materiel)s"""
                str_sql_delete_Id_materiel = """DELETE FROM t_materiel WHERE Id_materiel = %(value_Id_materiel)s"""
                #str_sql_delete_retour_materiel = """DELETE FROM t_retour_materiel WHERE fk_materiel = %(value_Id_materiel)s"""
                # Manière brutale d'effacer d'abord la "fk_materiel", même si elle n'existe pas dans la "t_preter_materiel"
                # Ensuite on peut effacer le materiel vu qu'il n'est plus "lié" (INNODB) dans la "t_preter_materiel"
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(str_sql_delete_preter_materiel, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_Id_materiel, valeur_delete_dictionnaire)
                    #mconn_bd.mabd_execute(str_sql_delete_retour_materiel, valeur_delete_dictionnaire)

                flash(f"materiel définitivement effacé !!", "success")
                print(f"materiel définitivement effacé !!")

                # afficher les données
                return redirect(url_for('materiels_afficher', order_by="ASC", Id_materiel_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_Id_materiel": id_materiel_delete}
            print(id_materiel_delete, type(id_materiel_delete))
            try:
                # Requête qui affiche tous les films qui ont le materiel que l'utilisateur veut effacer
                str_sql_materiels_films_delete = """SELECT Id_preter_materiel, nom, Id_materiel, materiel FROM t_preter_materiel 
                                                INNER JOIN t_client ON t_preter_materiel.fk_client = t_client.Id_client
                                                INNER JOIN t_materiel ON t_preter_materiel.fk_materiel = t_materiel.Id_materiel
                                                WHERE fk_materiel = %(value_Id_materiel)s"""

                mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

                mybd_curseur.execute(str_sql_materiels_films_delete, valeur_select_dictionnaire)
                data_films_attribue_materiel_delete = mybd_curseur.fetchall()
                print("data_films_attribue_materiel_delete...", data_films_attribue_materiel_delete)



            except (pymysql.err.OperationalError,

                    pymysql.ProgrammingError,

                    pymysql.InternalError,

                    pymysql.err.IntegrityError,

                    TypeError) as erreur_gest_genr_crud:
                # Requête qui affiche tous les films qui ont le materiel que l'utilisateur veut effacer
                str_sql_materiels_films_delete = """SELECT Id_retour_materiel, nom, Id_materiel, materiel FROM t_retour_materiel 
                                                                            INNER JOIN t_client ON t_retour_materiel.fk_client = t_client.Id_client
                                                                            INNER JOIN t_materiel ON t_retour_materiel.fk_materiel = t_materiel.Id_materiel
                                                                            WHERE fk_materiel = %(value_Id_materiel)s"""

                mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

                mybd_curseur.execute(str_sql_materiels_films_delete, valeur_select_dictionnaire)
                data_films_attribue_materiel_delete = mybd_curseur.fetchall()
                print("data_films_attribue_materiel_delete...", data_films_attribue_materiel_delete)

            # Nécessaire pour mémoriser les données afin d'afficher à nouveau
            # le formulaire "materiels/materiel_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
            session['data_films_attribue_materiel_delete'] = data_films_attribue_materiel_delete

            # Opération sur la BD pour récupérer "Id_materiel" et "materiel" de la "t_materiel"
            str_sql_Id_materiel = "SELECT Id_materiel, materiel FROM t_materiel WHERE Id_materiel = %(value_Id_materiel)s"

            mybd_curseur.execute(str_sql_Id_materiel, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()",
            # vu qu'il n'y a qu'un seul champ "nom materiel" pour l'action DELETE
            data_nom_materiel = mybd_curseur.fetchone()
            print("data_nom_materiel ", data_nom_materiel, " type ", type(data_nom_materiel), " materiel ",
                  data_nom_materiel["materiel"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "materiel_delete_wtf.html"
            form_delete.nom_materiel_delete_wtf.data = data_nom_materiel["materiel"]

            # Le bouton pour l'action "DELETE" dans le form. "materiel_delete_wtf.html" est caché.
            btn_submit_del = False

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans materiel_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans materiel_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")

        flash(f"Erreur dans materiel_delete_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")

        flash(f"__KeyError dans materiel_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("materiels/materiel_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_materiel_associes=data_films_attribue_materiel_delete)
