
from .app import manager, db
from datetime import datetime

@manager.command
def loaddb():
    """
    Generates database and fulfills it with false datas
    """

    from .models import Coordonnees, Utilisateur, Parterre, TypeMesure, TypePlante, Capteur, Donnee, Liste, Actions
    db.create_all() #Creating tables
    db.session.commit()

    l = Liste(idListe = 1)
    db.session.add(l)



    #Creation of users
    newuser(idU     = "tanguy",
            nomU    = "voiry",
            mdpU    = "test",
            prenomU = "tanguy")


    newuser(idU     = "florian",
            nomU    = "thomas",
            mdpU    = "test",
            prenomU = "florian")


    newuser(idU     = "maxime",
            nomU    = "deboffle",
            mdpU    = "test",
            prenomU = "maxime")


    newuser(idU     = "pierre",
            nomU    = "lemiere",
            mdpU    = "test",
            prenomU = "pierre")


    newuser(idU     = "joshua",
            nomU    = "vanoz",
            mdpU    = "test",
            prenomU = "joshua")

    #Creation of parterre "Bac à Sable" used to keep captors without parterre
    bac = Parterre(name = "Bac à sable")

    db.session.add(bac)
    c = Coordonnees(x        = 0,
                    y        = 0,
                    parterre = bac.get_id(),
                    num      = 0)
    bac.add_coordonnee(c)

    #Creation of TypeMesures
    typeM1 = TypeMesure(name = "Humidite")
    typeM2 = TypeMesure(name = "Temperature")
    db.session.add(typeM1)
    db.session.add(typeM2)

    #Creation of parterres
    p1 = Parterre(name        = "Parterre1")
    c1 = Coordonnees(x        = 6081088.3306859,
                     y        = 214343.058384172,
                     parterre = p1.get_id(),
                     num      = 0)
    p1.add_coordonnee(c1)

    c2 = Coordonnees(x        = 6080868.57422958,
                     y        = 214233.180156012,
                     parterre = p1.get_id(),
                     num      = 1)
    p1.add_coordonnee(c2)

    c3 = Coordonnees(x        = 6080682.25897314,
                     y        = 214596.256040366,
                     parterre = p1.get_id(),
                     num      = 2)
    p1.add_coordonnee(c3)

    c4 = Coordonnees(x        = 6080940.2339436,
                     y        = 214801.680553883,
                     parterre = p1.get_id(),
                     num      = 3)
    p1.add_coordonnee(c4)

    c5 = Coordonnees(x        = 6081088.3306859,
                     y        = 214343.058384172,
                     parterre = p1.get_id(),
                     num      = 4)
    p1.add_coordonnee(c5)

    db.session.add(p1)
    db.session.commit()

    #Creation of capteurs
    capteur = Capteur(name       = "capteur",
                      intervalle = 4,
                      tel        = "0123456789",
                      TypeMesure = typeM1.get_id(),
                      parterre   = p1.get_id())
    db.session.add(capteur)

    capteur2 = Capteur(name       = "Capteur2",
                      intervalle = 4,
                      tel        = "0123456789",
                      TypeMesure = typeM2.get_id(),
                      parterre   = p1.get_id())
    db.session.add(capteur2)

    db.session.commit()

    #Creation of TypePlantes
    plante1 = TypePlante(nomPlant = "Magnolia",
                     comportement = "Vivace",
                     taux_humidite = 0.8,
                     quantite = 10,
                     parterre_id = p1.get_id())
    p1.add_plante(plante1)

    plante2 = TypePlante(nomPlant = "Glaïeuls",
                     comportement = "Français",
                     taux_humidite = 0.5,
                     quantite = 15,
                     parterre_id = p1.get_id())
    p1.add_plante(plante2)

    #Creation of false datas
    donnee1 = Donnee(value   = 15,
                     date    = datetime.strptime('Jun 18 2018  10:14AM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee1)

    donnee2 = Donnee(value   = 25,
                     date    = datetime.strptime('Jun 18 2018  11:14AM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee2)

    donnee3 = Donnee(value   = 12,
                     date    = datetime.strptime('Jun 18 2018  12:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee3)

    donnee4 = Donnee(value   = 3,
                     date    = datetime.strptime('Jun 18 2018  10:14AM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee4)

    donnee5 = Donnee(value   = 42,
                     date    = datetime.strptime('Jun 18 2018  11:14AM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee5)

    donnee6 = Donnee(value   = 56,
                     date    = datetime.strptime('Jun 18 2018  12:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee6)

    donnee7 = Donnee(value   = 23,
                     date    = datetime.strptime('Jun 18 2018  1:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee7)

    donnee8 = Donnee(value   = 16,
                     date    = datetime.strptime('Jun 18 2018  2:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee8)

    donnee9 = Donnee(value   = 8,
                     date    = datetime.strptime('Jun 18 2018  3:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee9)

    donnee10 = Donnee(value   = 2,
                     date    = datetime.strptime('Jun 18 2018  1:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee10)

    donnee11 = Donnee(value   = 5,
                     date    = datetime.strptime('Jun 18 2018  2:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee11)

    donnee12 = Donnee(value   = 35,
                     date    = datetime.strptime('Jun 18 2018  3:14PM', '%b %d %Y %I:%M%p'),
                     capteur = capteur2.get_id(),
                     parterre = p1.get_id())
    db.session.add(donnee12)

    db.session.commit()


@manager.command
def syncdb():
    """
    Creates all mising tables
    """
    db.create_all()

@manager.command
def newuser(idU,nomU,mdpU,prenomU):
    """
    Adds a new user
    """

    from .models import Utilisateur
    from hashlib import sha256
    m = sha256()
    m.update(mdpU.encode())
    u=Utilisateur(idU=idU,nomU=nomU,mdpU=m.hexdigest(),prenomU=prenomU)
    db.session.add(u)
    db.session.commit()

@manager.command
def passwd(username,password):
    """
    Changes the password of the user username by password
    """
    from .models import User,get_user
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    user=get_user(username)
    user.password=m.hexdigest()
    db.session.commit()
