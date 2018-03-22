from .app import app, db
from flask import render_template, url_for, redirect, request
from .models import *
from .formulaires import *
from flask_wtf import FlaskForm
from wtforms import StringField,HiddenField,PasswordField
from wtforms.validators import DataRequired
from flask_login import login_user,current_user, logout_user, login_required

@app.route("/")
def home():
    return render_template(
        "home.html",
        title = "Capteurs",
        liste = get_listeActions(1))

@app.route("/Parterre/")
def parterre():
    return render_template(
        "mesParterre.html",
        mesParterre = get_parterres(),
        title       = "Liste des Parterres")

@app.route("/login/", methods = ("GET","POST",))
def login():
	f = LoginForm()
	if not f.is_submitted():
		f.set_next(request.args.get("next"))
	elif f.validate_on_submit():
		user = f.get_authenticated_user()
		if user:
			login_user(user)
			next = f.get_next() or url_for("home")
			return redirect(next)
	return render_template(
        "login.html",
        form  = f,
        title = "Connexion")

@app.route("/inscription/", methods = ("GET","POST",))
def inscription():
    f = InscriptionForm()
    return render_template(
        "inscription.html",
        form = f,
        title = "Inscription")

@app.route("/inscription/save/", methods=["POST"])
def save_inscription():
    user = None
    f = InscriptionForm()
    if f.validate_on_submit() and f.uniq_Username() and f.passwd_confirmed():
        from hashlib import sha256
        m = sha256()
        m.update(f.get_mdp().encode())
        user = Utilisateur(
            idU     = f.get_id(),
            mdpU    = m.hexdigest(),
            nomU    = f.get_name(),
            prenomU = f.get_surname())
        db.session.add(user)
        i = Actions(
            contenu = "Bienvenue à "+f.get_id(),
            liste = 1
        )
        db.session.add(i)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(
		"inscription.html",
		form  = f,
        title = "Inscription")

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/Contacts/")
def contacts():
    return render_template(
        "contacts.html",
        title = "Contacts")

@app.route("/Parterre/info/<int:id>")
def parterre_info(id):
    parterre = get_parterre(id)
    return render_template(
        "parterre-info.html",
        parterre = parterre,
        title    = parterre.get_name(),
        capteurs = get_capteurs_parterre(id))

@app.route("/Capteur/")
def capteur():
    return render_template(
        "capteur.html",
        mesCapteurs = get_capteurs(),
        title = "Liste des Capteurs")


@app.route("/Capteur/info/<int:id>")
def capteur_info(id):
    capteur = get_capteur(id)
    return render_template(
        "capteur-info.html",
        capteur  = capteur,
        title    = capteur.get_name(),
        parterre = get_parterre(capteur.get_parterre()),
        mesure   = get_typeMesure(capteur.get_typeMesure()))

@app.route("/Capteur/info/Relever/<int:id>",methods=("POST","GET"))
def capteur_info_relever(id):
    if id==0:
        id=request.form['del']
    print(id)
    capteur = get_capteur(id)
    return render_template(
        "relever-capteur.html",
        capteur  = capteur)


@app.route("/Relever/Capteur/")
def capteur_info_relever1():
    return render_template(
        "relever_capt.html",
        liste = get_capteurs())

@app.route("/Ajouter/Capteur/")
@login_required
def add_Capteur():
    f = CapteurForm()
    return render_template(
        "addCapteur.html",
        form  = f,
        title = "Nouveau capteur",
        param = "create")

@app.route("/Ajouter/Capteur/Parterre/<int:id>")
@login_required
def add_Capteur_Part(id):
    f = CapteurForm()
    return render_template(
        "addCapteur.html",
        form  = f,
        parterre = id,
        title = "Nouveau capteur",
        param = "createPart")

@app.route("/Ajouter/Capteur/saving/", methods=("POST",))
def new_capteur_saving():
    """
    Saves the new capteur in the database and redirect the user to his home page.
    """
    f = CapteurForm()
    if f.validate_on_submit():
        o = Capteur(
            name       = f.get_name(),
            intervalle = f.get_interval(),
            tel        = f.get_phoneNumber(),
            TypeMesure = f.get_typeMesure().get_id(),
            parterre   = f.get_parterre().get_id())
        a = Actions(
            contenu = "Ajout d'un nouveau capteur "+f.get_name(),
            liste = 1
        )
        db.session.add(a)
        db.session.add(o)
        db.session.commit()
        return redirect(url_for('capteur_info', id = o.get_id()))
    return render_template(
        "addCapteur.html",
        form  = f,
        title = "Nouveau capteur",
        param = "create")

@app.route("/Supprimer/Capteur", methods = ["POST","GET"])
@login_required
def delete_capteur():
    if request.method=="POST":
        if request.form['del']=="":
            return render_template(
                "delete-capteur.html",
                liste = get_capteurs(),
                title = "Supprimer un capteur")
        else:
            a = get_capteur(int(request.form['del']))
            a.clear_datas()
            ac = Actions(
                contenu = "Suppresion du capteur "+a.get_name(),
                liste = 1
            )
            db.session.add(ac)
            db.session.delete(a)
            db.session.commit()
    return render_template(
        "delete-capteur.html",
        liste = get_capteurs(),
        title = "Supprimer un capteur")

@app.route("/Supprimer/Parterre", methods = ["POST","GET"])
@login_required
def delete_part():
    if request.method=="POST":
        if request.form['del']=="":
            return render_template(
                "delete-parterre.html",
                liste = get_parterres(),
                title = "Supprimer un parterre")
        else:
            a = get_parterre(int(request.form['del']))
            a.clear_datas()
            for capteur in a.get_capteurs():
                a.delete_capteur(capteur)
                capteur.set_parterre(1)
            p = Actions(
                contenu = "Suppresion du parterre "+a.get_name(),
                liste = 1
            )
            db.session.add(p)
            db.session.delete(a)
            db.session.commit()
    return render_template(
        "delete-parterre.html",
        liste = get_parterres(),
        title = "Supprimer un parterre")

@app.route("/Supprimer/Capteur/<int:id>")
@login_required
def delete_cap(id):
    capteur = get_capteur(id)
    capteur.clear_datas()
    a = Actions(
        contenu = "Suppresion du capteur "+capteur.get_name(),
        liste = 1
    )
    db.session.add(a)
    db.session.delete(capteur)
    db.session.commit()
    return redirect(url_for("capteur"))


@app.route("/Ajouter/Parterre/")
@login_required
def add_Parterre():
    f = ParterreForm()
    return render_template(
        "create-parterre.html",
        form  = f,
        title = "Ajouter un nouveau Parterre",
        param = "create")

@app.route("/Ajouter/Parterre/saving/", methods=("POST",))
def new_parterre_saving():
    f = ParterreForm()
    if f.validate_on_submit():
        o = Parterre(name = f.get_name())
        db.session.add(o)
        form = request.form
        longitudes = form.getlist("longitudes")
        latitudes  = form.getlist("latitudes")
        num = 0
        for longitude,latitude in zip(longitudes, latitudes):
            c = Coordonnees(x        = longitude,
                            y        = latitude,
                            parterre = o.get_id(),
                            num      = num)
            num = num+1
            try:
                o.add_coordonnee(c)
            except Exception as e:
                db.session.rollback()
        p = Actions(
            contenu = "Ajout d'un nouveau parterre "+f.get_name(),
            liste = 1
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('parterre_info', id = o.get_id()))
    return render_template(
        "create-parterre.html",
        form  = f,
        title = "Ajouter un nouveau Parterre",
        param = "create")

@app.route("/Capteur/edit/<int:id>")
def edit_capteur(id):
    capteur = get_capteur(id)
    form = CapteurForm(capteur)
    return render_template(
        "addCapteur.html",
        title = capteur.get_name()+" - edit",
        form  = form,
        capteur = capteur,
        param = "modif")

@app.route("/Capteur/save/", methods = ("POST",))
def save_capteur():
    f = CapteurForm()
    a = get_capteur(f.get_id())
    na = a.get_name()
    if f.validate_on_submit():
        a.set_name(f.get_name())
        a.set_num(f.get_phoneNumber())
        a.set_interval(f.get_interval())
        if a.get_parterre() != f.get_parterre().get_id():
            a.set_parterre(f.get_parterre().get_id())
        if a.get_typeMesure() != f.get_typeMesure().get_id():
            a.set_typeMesure(f.get_typeMesure().get_id())
        ac = Actions(
            contenu = "Modification du capteur "+na+" -> "+a.get_name(),
            liste = 1
        )
        db.session.add(ac)
        db.session.commit()
        return redirect(url_for(
            "capteur_info",
            id    = f.get_id()))
    f.next.data = "save_capteur"
    return render_template(
        "addCapteur.html",
        title = a.get_name()+" - edit",
        form  = f,
        capteur=a,
        param = "modif")

@app.route("/Parterre/edit/<int:id>")
def edit_parterre(id):
    parterre = get_parterre(id)
    form = ParterreForm(parterre)
    return render_template("create-parterre.html",
                title= parterre.get_name()+"  - edit",
                form = form,
                parterre = parterre,
                param = "modif")

@app.route("/Parterre/save/", methods = ("POST",))
def save_parterre():
    f= ParterreForm()
    a = get_parterre(f.get_id())
    na = a.get_name()
    if f.validate_on_submit():
        a.set_name(f.get_name())
        form = request.form
        longitudes = form.getlist("longitudes")
        if longitudes != []:
            latitudes  = form.getlist("latitudes")
            num = 0
            a.remove_coordonnees()
            for longitude,latitude in zip(longitudes, latitudes):
                c = Coordonnees(x        = longitude,
                                y        = latitude,
                                parterre = a.get_id(),
                                num      = num)
                num = num+1
                a.add_coordonnee(c)
        p = Actions(
            contenu = "Modification du parterre "+na+" -> "+a.get_name(),
            liste = 1
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for("parterre_info", id = a.get_id()))
    f.next.data = "save_parterre"
    return render_template("create-parterre.html",
                title= a.get_name()+"  - edit",
                form = f,
                parterre = a,
                param = "modif")

@app.route("/Supprimer/Parterre/<int:id>")
def delete_parterre(id):
    a   = get_parterre(id)
    bac = get_bac_a_sable()
    for capteur in a.get_capteurs():
        capteur.set_parterre(bac.get_id())
    a.remove_coordonnees()
    a.clear_datas()
    db.session.delete(a)
    p = Actions(
        contenu = "Suppresion du parterre "+a.get_name(),
        liste = 1
    )
    db.session.add(p)
    db.session.commit()
    return redirect(url_for("parterre"))

@app.route("/Ajouter/Plante/<int:id>")
@login_required
def add_Plante(id):
    f = PlanteForm()
    return render_template(
        "create-plante.html",
        form  = f,
        title = "Nouvelle Plante",
        param = "create",
        parterre = id)

@app.route("/Ajouter/Plante/saving/", methods=("POST",))
def new_plante_saving():
    """
    Saves the new plant in the database and redirect the user to his home page.
    """
    f = PlanteForm()
    if f.validate_on_submit():
        o = TypePlante(
            nomPlant = f.get_name(),
            comportement = f.get_comportement(),
            taux_humidite = f.get_taux_humidite(),
            quantite = f.get_quantite(),
            parterre_id = f.get_parterre().get_id())
        f.get_parterre().add_plante(o)
        db.session.add(o)
        p = Actions(
            contenu = "Ajout d'une plante "+f.get_name() + " au parterre "+ f.get_parterre().get_name(),
            liste = 1
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('parterre_info', id = o.get_parterre()))
    return render_template(
        "create-plante.html",
        form  = f,
        parterre = f.get_parterre().get_id(),
        title = "Nouvelle plante",
        param = "create")

@app.route("/Plante/save/", methods = ("POST",))
def save_plante():
    f = PlanteForm()
    f.parterre.data = get_parterre(get_plante(f.get_id()).get_parterre())
    a = get_plante(f.get_id())
    if f.validate_on_submit():
        a.set_name(f.get_name())
        a.set_comportement(f.get_comportement())
        a.set_taux_humidite(f.get_taux_humidite())
        a.set_quantite(f.get_quantite())
        p = Actions(
            contenu = "Modification de la plante "+a.get_name() + " du parterre "+ a.get_parterre().get_name(),
            liste = 1
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for(
            "plante_info", id = f.get_id()))
    f.next.data = "save_plante"
    return render_template(
        "create-plante.html",
        title = a.get_name()+" - edit",
        form  = f,
        plante = a,
        param = "modif")

@app.route("/Plante/info/<int:id>")
def plante_info(id):
    plante = get_plante(id)
    return render_template(
        "plante-info.html",
        plante = plante,
        title = plante.get_name(),
        parterre = get_parterre(plante.get_parterre()))

@app.route("/Supprimer/Plante/<int:id>")
def delete_plante(id):
    plante = get_plante(id)
    db.session.delete(plante)
    get_parterre(plante.get_parterre()).delete_plante(plante)
    p = Actions(
        contenu = "Suppression de la plante "+plante.get_name() + " au parterre "+ plante.get_parterre().get_name(),
        liste = 1
    )
    db.session.add(p)
    db.session.commit()
    return redirect(url_for("parterre"))

@app.route("/Modifier/Plante/<int:id>")
def edit_plante(id):
    plante = get_plante(id)
    form = PlanteForm(plante)
    return render_template(
        "create-plante.html",
        title = plante.get_name()+" - edit",
        form  = form,
        plante = plante,
        param = "modif")
