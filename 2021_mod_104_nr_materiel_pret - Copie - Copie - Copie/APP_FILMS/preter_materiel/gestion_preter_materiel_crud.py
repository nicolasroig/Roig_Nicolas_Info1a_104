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
from APP_FILMS.preter_materiel.gestion_preter_materiel_wtf_forms import FormWTFAjouterpretermateriel
from APP_FILMS.preter_materiel.gestion_preter_materiel_wtf_forms import FormWTFDeletepretermateriel
from APP_FILMS.preter_materiel.gestion_preter_materiel_wtf_forms import FormWTFUpdatepretermateriel

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /client_afficher
    
    Test : ex : http://127.0.0.1:5005/materiels_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                Id_client_sel = 0 >> tous les materiels.
                Id_client_sel = "n" affiche le client dont l id est "n"
"""


@obj_mon_application.route("/preter_materiel_afficher/<string:order_by>/<int:Id_preter_materiel_sel>", methods=['GET', 'POST'])
def preter_materiel_afficher(order_by, Id_preter_materiel_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion clients ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur Gestionclients {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                if order_by == "ASC" and Id_preter_materiel_sel == 0:
                    strsql_preter_materiel_afficher = """SELECT Id_preter_materiel, etat_avant_pret, date_pret FROM t_preter_materiel
                     ORDER BY Id_client ASC"""
                    mc_afficher.execute(strsql_preter_materiel_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_materiel"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du client sélectionné avec un nom de variable
                    valeur_Id_preter_materiel_selected_dictionnaire = {"value_Id_preter_materiel_selected": Id_preter_materiel_sel}
                    strsql_preter_materiel_afficher = """SELECT Id_preter_materiel, etat_avant_pret, date_pret FROM t_preter_materiel 
                    WHERE Id_preter_materiel = %(value_Id_preter_materiel_selected)s"""

                    mc_afficher.execute(strsql_preter_materiel_afficher, valeur_Id_preter_materiel_selected_dictionnaire)
                else:
                    strsql_preter_materiel_afficher = """SELECT Id_preter_materiel, etat_avant_pret, date_pret     
                    FROM t_preter_materiel ORDER BY Id_preter_materiel DESC"""

                    mc_afficher.execute(strsql_preter_materiel_afficher)

                data_preter_materiel = mc_afficher.fetchall()

                print("data_preter_materiel ", data_preter_materiel, " Type : ", type(data_preter_materiel))

                # Différencier les messages si la table est vide.
                if not data_preter_materiel and Id_preter_materiel_sel == 0:
                    flash("""La table "t_preter_materiel" est vide. !!""", "warning")
                elif not data_preter_materiel and Id_preter_materiel_sel > 0:
                    # Si l'utilisateur change l'id_materiel dans l'URL et que le materiel n'existe pas,
                    flash(f"Le preter_materiel n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_materiel" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données preter_materiel affichés !!", "success")

        except Exception as erreur:
            print(f"RGG Erreur générale. preter_materiel_afficher")
            # OM 2020.04.09 On dérive "Exception" par le "@obj_mon_application.errorhandler(404)"
            # fichier "run_mon_app.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            flash(f"RGG Exception {erreur} preter_materiel_afficher", "danger")
            raise Exception(f"RGG Erreur générale. {erreur}")
            # raise MaBdErreurOperation(f"RGG Exception {msg_erreurs['ErreurNomBD']['message']} {erreur}")

    # Envoie la page "HTML" au serveur.
    return render_template("preter_materiel/preter_materiel_afficher.html", data=data_preter_materiel)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /client_ajouter
    
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


@obj_mon_application.route("/client_ajouter", methods=['GET', 'POST'])
def client_ajouter_wtf():
    form = FormWTFAjouterclients()
    if request.method == "POST":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion clients ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur Gestionclients {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            if form.validate_on_submit():
                name_clients_wtf = form.nom_clients_wtf.data
                name_prenom_wtf = form.prenom_wtf.data

                name_clients = name_clients_wtf.lower()
                name_prenom = name_prenom_wtf.lower()
                valeurs_insertion_dictionnaire = {"value_prenom": name_prenom,
                                                  "value_clients": name_clients}
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                # INSERT INTO `t_client` (`Id_client`, `nom`, `prenom`) VALUES (NULL, 'diogo', 'jota');
                strsql_insert_client = """INSERT INTO t_client (Id_client,nom, prenom) 
                VALUES (NULL,%(value_clients)s,%(value_prenom)s)"""
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(strsql_insert_client, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('client_afficher', order_by='DESC', Id_client_sel=0))

        # ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except pymysql.err.IntegrityError as erreur_clients_doublon:
            # Dérive "pymysql.err.IntegrityError" dans "MaBdErreurDoublon" fichier "erreurs/exceptions.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            code, msg = erreur_clients_doublon.args

            flash(f"{error_codes.get(code, msg)} ", "warning")

        # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except (pymysql.err.OperationalError,
                pymysql.ProgrammingError,
                pymysql.InternalError,
                TypeError) as erreur_gest_genr_crud:
            code, msg = erreur_gest_genr_crud.args

            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Erreur dans Gestion clients CRUD : {sys.exc_info()[0]} "
                  f"{erreur_gest_genr_crud.args[0]} , "
                  f"{erreur_gest_genr_crud}", "danger")

    return render_template("clients/client_ajouter_wtf.html", form=form)


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


@obj_mon_application.route("/client_update", methods=['GET', 'POST'])
def client_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_materiel"
    id_client_update = request.values['id_client_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateclients()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "client_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            name_client_update = form_update.nom_client_update_wtf.data
            name_prenom_update = form_update.prenom_update_wtf.data

            name_client_update = name_client_update.lower()
            name_prenom_update = name_prenom_update.lower()

            valeur_update_dictionnaire = {"value_Id_client": id_client_update,
                                          "value_name_clients": name_client_update,
                                          "value_prenom": name_prenom_update}

            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            #UPDATE `t_client` SET `prenom` = 'Johnn' WHERE `t_client`.`Id_client` = 1;
            str_sql_update_clients = """UPDATE t_client SET nom = %(value_name_clients)s, prenom = %(value_prenom)s WHERE t_client . Id_client = %(value_Id_client)s"""
            with MaBaseDeDonnee() as mconn_bd:
                mconn_bd.mabd_execute(str_sql_update_clients, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_materiel_update"
            return redirect(url_for('client_afficher', order_by="ASC", Id_client_sel=id_client_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_materiel" et "materiel" de la "t_materiel"
            str_sql_Id_clients = "SELECT Id_client, nom, prenom FROM t_client WHERE Id_client = %(value_Id_client)s"
            valeur_select_dictionnaire = {"value_Id_client": id_client_update}
            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()
            mybd_curseur.execute(str_sql_Id_clients, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom materiel" pour l'UPDATE
            data_client = mybd_curseur.fetchone()
            print(data_client)
            print("data_nom_client ", data_client, " type ", type(data_client), " client ",
                  data_client["client"])
            print("data_nom_prenom ", data_client, " type ", type(data_client), " prenom ",
                  data_client["prenom"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "materiel_update_wtf.html"
            form_update.nom_client_update_wtf.data = data_client["client"]
            form_update.prenom_update_wtf.data = data_client["prenom"]

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans client_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
        flash(f"__KeyError dans prenom_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans client_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
        flash(f"Erreur dans prenom_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")
        flash(f"Erreur dans client_update_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")
        flash(f"__KeyError dans client_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("clients/client_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /client_delete
    
    Test : ex. cliquer sur le menu "client" puis cliquer sur le bouton "DELETE" d'un "client"
    
    Paramètres : sans
    
    But : Effacer(delete) un client qui a été sélectionné dans le formulaire "materiels_afficher.html"
    
    Remarque :  Dans le champ "nom_materiel_delete_wtf" du formulaire "materiels/materiel_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@obj_mon_application.route("/client_delete", methods=['GET', 'POST'])
def client_delete_wtf():
    data_films_attribue_client_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_materiel"
    id_client_delete = request.values['id_client_btn_delete_html']

    # Objet formulaire pour effacer le materiel sélectionné.
    form_delete = FormWTFDeleteclients()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("client_afficher", order_by="ASC", Id_client_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "materiels/materiel_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_client_delete = session['data_films_attribue_client_delete']
                print("data_films_attribue_client_delete ", data_films_attribue_client_delete)

                flash(f"Effacer le client de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer materiel" qui va irrémédiablement EFFACER le materiel
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_Id_client": id_client_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_preter_materiel = """DELETE FROM t_preter_materiel WHERE fk_client = %(value_Id_client)s"""
                str_sql_delete_Id_client = """DELETE FROM t_client WHERE Id_client = %(value_Id_client)s"""
                #str_sql_delete_retour_materiel = """DELETE FROM t_retour_materiel WHERE fk_materiel = %(value_Id_materiel)s"""
                # Manière brutale d'effacer d'abord la "fk_materiel", même si elle n'existe pas dans la "t_preter_materiel"
                # Ensuite on peut effacer le materiel vu qu'il n'est plus "lié" (INNODB) dans la "t_preter_materiel"
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(str_sql_delete_preter_materiel, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_Id_client, valeur_delete_dictionnaire)
                    #mconn_bd.mabd_execute(str_sql_delete_retour_materiel, valeur_delete_dictionnaire)

                flash(f"materiel définitivement effacé !!", "success")
                print(f"materiel définitivement effacé !!")

                # afficher les données
                return redirect(url_for('client_afficher', order_by="ASC", Id_client_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_Id_client": id_client_delete}
            print(id_client_delete, type(id_client_delete))
            try:
                # Requête qui affiche tous les films qui ont le materiel que l'utilisateur veut effacer
                str_sql_client_films_delete = """SELECT Id_preter_materiel, date_pret, Id_client, nom FROM t_preter_materiel 
                                                INNER JOIN t_materiel ON t_preter_materiel.fk_materiel = t_materiel.Id_materiel
                                                INNER JOIN t_client ON t_preter_materiel.fk_client = t_client.Id_client
                                                WHERE fk_client = %(value_Id_client)s"""

                mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

                mybd_curseur.execute(str_sql_client_films_delete, valeur_select_dictionnaire)
                data_films_attribue_client_delete = mybd_curseur.fetchall()
                print("data_films_attribue_client_delete...", data_films_attribue_client_delete)



            except (pymysql.err.OperationalError,

                    pymysql.ProgrammingError,

                    pymysql.InternalError,

                    pymysql.err.IntegrityError,

                    TypeError) as erreur_gest_genr_crud:
                # Requête qui affiche tous les films qui ont le materiel que l'utilisateur veut effacer
                str_sql_client_films_delete = """SELECT Id_preter_materiel, nom, Id_client, prenom FROM t_preter_materiel 
                                                INNER JOIN t_materiel ON t_preter_materiel.fk_materiel = t_materiel.Id_materiel
                                                INNER JOIN t_client ON t_preter_materiel.fk_client = t_client.Id_client
                                                WHERE fk_client = %(value_Id_client)s"""

                mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

                mybd_curseur.execute(str_sql_client_films_delete, valeur_select_dictionnaire)
                data_films_attribue_client_delete = mybd_curseur.fetchall()
                print("data_films_attribue_client_delete...", data_films_attribue_client_delete)

            # Nécessaire pour mémoriser les données afin d'afficher à nouveau
            # le formulaire "materiels/materiel_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
            session['data_films_attribue_client_delete'] = data_films_attribue_client_delete

            # Opération sur la BD pour récupérer "Id_materiel" et "materiel" de la "t_materiel"
            str_sql_Id_clients = "SELECT Id_client, client FROM t_client WHERE Id_client = %(value_Id_client)s"

            mybd_curseur.execute(str_sql_Id_clients, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()",
            # vu qu'il n'y a qu'un seul champ "nom materiel" pour l'action DELETE
            data_nom_client = mybd_curseur.fetchone()
            print("data_nom_client ", data_nom_client, " type ", type(data_nom_client), " client ",
                  data_nom_client["client"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "materiel_delete_wtf.html"
            form_delete.nom_client_delete_wtf.data = data_nom_client["client"]

            # Le bouton pour l'action "DELETE" dans le form. "materiel_delete_wtf.html" est caché.
            btn_submit_del = False

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans client_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans client_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")

        flash(f"Erreur dans client_delete_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")

        flash(f"__KeyError dans client_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("clients/client_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_materiel_associes=data_films_attribue_client_delete)
