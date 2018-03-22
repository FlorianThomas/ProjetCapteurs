from .app import db,login_manager
from flask_login import UserMixin
import datetime

class Utilisateur(db.Model, UserMixin):
    """
    Only users can interact with the database and the application.
    """
    idU     = db.Column(db.String(50), primary_key=True)
    mdpU    = db.Column(db.String(100))
    nomU    = db.Column(db.String(20))
    prenomU = db.Column(db.String(20))

    def __init__(self, idU, mdpU, nomU, prenomU):
        self.idU     = idU
        self.mdpU    = mdpU
        self.nomU    = nomU
        self.prenomU = prenomU

    def __repr__(self):
        return "<Utilisateur (%d) %s>" % (self.idU, self.nomU)

    def get_name(self):
        return self.nomU

    def get_id(self):
        return self.idU

    def get_mdp(self):
        return self.mdpU

    def get_surname(self):
        return self.prenomU

    def set_name(self,nomU):
        self.nomU = nomU

    def set_firstname(self,prenomU):
        self.prenomU = prenomU

    def set_mdp(self,mdpU):
        self.mdpU = mdpU

association_parterre_typePlante = db.Table("association_parterre_typePlante",
                                           db.metadata,
                                           db.Column("parterre_id", db.Integer, db.ForeignKey("parterre.idP"), primary_key = True),
                                           db.Column("type_plante_id", db.Integer, db.ForeignKey("type_plante.idPlant"), primary_key = True))

association_parterre_capteur = db.Table("association_parterre_capteur",
                                        db.metadata,
                                        db.Column("parterre_id", db.Integer, db.ForeignKey("parterre.idP"), primary_key = True),
                                        db.Column("capteur_id", db.Integer, db.ForeignKey("capteur.idCapt"), primary_key = True))

association_parterre_coordonnee = db.Table("association_parterre_coordonnee",
                                        db.metadata,
                                        db.Column("parterre_id", db.Integer, db.ForeignKey("parterre.idP"), primary_key = True),
                                        db.Column("coord_id", db.Integer, db.ForeignKey("coordonnees.coord_id"), primary_key = True))

association_capteur_donnee = db.Table("association_capteur_donnee",
                                      db.metadata,
                                      db.Column("capteur_id", db.Integer, db.ForeignKey("capteur.idCapt"), primary_key = True),
                                      db.Column("donnee_id", db.Integer, db.ForeignKey("donnee.idDonnee"), primary_key = True))

association_liste_actions=db.Table("association_liste_actions",
                                    db.metadata,
                                    db.Column("idListe", db.Integer, db.ForeignKey("liste.idListe"), primary_key = True),
                                    db.Column("idActions", db.Integer, db.ForeignKey("actions.idActions"),primary_key=True))

class Coordonnees(db.Model):
    """
    Coordinates can specify the position of a parterre
    """
    coord_id    = db.Column(db.Integer, primary_key = True)
    longitude   = db.Column(db.Float)
    latitude    = db.Column(db.Float)
    numero      = db.Column(db.Integer)

    def __init__(self, x, y, parterre, num):
        self.longitude = x
        self.latitude  = y
        self.parterre  = parterre
        self.numero    = num

    def get_X(self):
        return self.longitude

    def get_Y(self):
        return self.latitude

class Parterre(db.Model):
    """
    A Parterre have a list of Capteurs, is located by Coordonnees and contains a list of TypePlantes
    """
    idP         = db.Column(db.Integer, primary_key=True)
    nomP        = db.Column(db.String(100))
    plantes     = db.relationship("TypePlante",
                                  secondary = association_parterre_typePlante,
                                  lazy      = "dynamic",
                                  backref   = db.backref("TypePlante", lazy = True))
    capteurs    = db.relationship("Capteur",
                                  secondary = association_parterre_capteur,
                                  lazy      = "dynamic",
                                  backref   = db.backref("Capteur", lazy = True))
    coordonnees = db.relationship("Coordonnees",
                                  secondary = association_parterre_coordonnee,
                                  lazy      = "dynamic",
                                  backref   = db.backref("Coordonnees", lazy = True),
                                  order_by  = "Coordonnees.numero")

    def __init__(self, name):
        self.nomP = name

    def __repr__(self):
        return "<Parterre (%d) %s>" % (self.idP, self.nomP)

    def get_name(self):
        return self.nomP

    def get_id(self):
        return self.idP

    def get_coordonnees(self):
        return self.coordonnees

    def get_capteurs(self):
        return self.capteurs

    def get_plantes(self):
        return self.plantes

    def set_name(self,nomP):
        self.nomP = nomP

    def remove_coordonnees(self):
        for coord in self.get_coordonnees():
            self.coordonnees.remove(coord)
            db.session.delete(coord)

    def add_coordonnee(self, coord):
        self.coordonnees.append(coord)

    def add_capteur(self, capteur):
        self.capteurs.append(capteur)

    def add_plante(self, plante):
        self.plantes.append(plante)

    def delete_capteur(self, capteur):
        if capteur in self.capteurs:
            self.capteurs.remove(capteur)

    def delete_plante(self, plante):
        if plante in self.plantes:
            self.plantes.remove(plante)

    def clear_datas(self):
        """
        suppress all datas of the parterre
        """
        liste = Donnee.query.filter(Donnee.idParterre == self.idP)
        for donnee in liste:
            db.session.delete(donnee)

class TypePlante(db.Model):
    """
    A TypePlante is contained in a Parterre. If the Parterre is deleted, plants are deleted too.
    """
    idPlant  = db.Column(db.Integer, primary_key=True)
    nomPlant = db.Column(db.String(100))
    comportement = db.Column(db.String(200))
    taux_humidite = db.Column(db.Float)
    quantite = db.Column(db.Integer)
    parterre_id = db.Column(db.Integer, db.ForeignKey("parterre.idP"))

    def __init__(self, nomPlant, comportement, taux_humidite, quantite, parterre_id):
        self.nomPlant      = nomPlant
        self.comportement  = comportement
        self.taux_humidite = taux_humidite
        self.quantite      = quantite
        self.parterre_id   = parterre_id

    def __repr__(self):
        return "<TypePlante (%d) %s>" % (self.nomPlant)

    def get_name(self):
        return self.nomPlant

    def get_id(self):
        return self.idPlant

    def set_name(self,NomPlant):
        self.nomPlant = NomPlant

    def get_comportement(self):
        return self.comportement

    def set_comportement(self, NewComport):
        self.comportement = NewComport

    def get_taux_humidite(self):
        return self.taux_humidite

    def set_taux_humidite(self, NewTaux):
        self.taux_humidite = NewTaux

    def get_quantite(self):
        return self.quantite

    def set_quantite(self, NewQuantite):
        self.quantite = NewQuantite

    def get_parterre(self):
        return self.parterre_id



class TypeMesure(db.Model):
    """
    A TypeMesure is important to know how to use datas sended by Capteurs
    """
    id_typeM  = db.Column(db.Integer, primary_key=True)
    nom_typeM = db.Column(db.String(100))

    def __init__(self, name):
        self.nom_typeM = name

    def __repr__(self):
        return "<TypeMesure (%d) %s>" % (self.id_typeM, self.nom_typeM)

    def get_name(self):
        return self.nom_typeM

    def get_id(self):
        return self.id_typeM

    def set_name(self,nomTypeM):
        self.nom_typeM = nomTypeM

class Capteur(db.Model):
    """
    A Capteur is updates its position and its lvlBatCapt itself.
    It is placed when he's added in the database.
    He generates a list of datas at the intervalleTemps between each.
    """
    idCapt          = db.Column(db.Integer, primary_key=True)
    nomCapt         = db.Column(db.String(20))
    lieuGeoCaptX    = db.Column(db.Float)
    lieuGeoCaptY    = db.Column(db.Float)
    lvlBatCapt      = db.Column(db.Integer)
    datePlacement   = db.Column(db.DateTime)
    intervalleTemps = db.Column(db.Integer)
    numTel          = db.Column(db.String(10))
    typeM_id        = db.Column(db.Integer, db.ForeignKey("type_mesure.id_typeM"))
    parterre_id     = db.Column(db.Integer, db.ForeignKey("parterre.idP"))
    listeDonnees    = db.relationship("Donnee",
                                      secondary = "association_capteur_donnee",
                                      lazy = "dynamic",
                                      backref = db.backref("donnee", lazy = "dynamic"),
                                      order_by  = "Donnee.dateRel")

    def __init__(self, name, intervalle, tel, TypeMesure, parterre):
        self.nomCapt         = name
        self.lieuGeoCaptX    = 51.25
        self.lieuGeoCaptY    = 45.2
        self.lvlBatCapt      = 50
        self.numTel          = tel
        self.datePlacement   = datetime.datetime.now()
        self.intervalleTemps = intervalle
        self.typeM_id        = TypeMesure
        self.parterre_id     = parterre
        get_parterre(parterre).add_capteur(self)

    def __repr__(self):
        return "<Capteur (%d) %s>" % (self.idCapt, self.nomCapt)

    def get_name(self):
        return self.nomCapt

    def get_id(self):
        return self.idCapt

    def get_coordonnees(self):
        return (self.lieuGeoCaptX, self.lieuGeoCaptY)

    def get_date(self):
        dateP = str(self.datePlacement)[:10]+"  |  "+str(self.datePlacement)[11:16]
        return dateP

    def get_lvlBattery(self):
        return self.lvlBatCapt

    def get_interval(self):
        return self.intervalleTemps

    def get_typeMesure(self):
        return self.typeM_id

    def get_phoneNumber(self):
        return self.numTel

    def get_parterre(self):
        return self.parterre_id

    def get_vals(self):
        return self.listeDonnees

    def set_name(self,nomCapt):
        self.nomCapt = nomCapt

    def set_X(self,lieuGeoCaptX):
        self.lieuGeoCaptX = lieuGeoCaptX

    def set_Y(self,lieuGeoCaptY):
        self.lieuGeoCaptY = lieuGeoCaptY

    def set_num(self,numTel):
        self.numTel = numTel

    def set_interval(self, newInterval):
        self.intervalleTemps = newInterval

    def set_lvlBattery(self, newVal):
        self.lvlBattery = newVal

    def set_typeMesure(self, newType):
        self.typeM_id = newType

    def set_parterre(self, newParterre):
        if self.parterre_id != None:
            get_parterre(self.parterre_id).delete_capteur(self)
        self.parterre_id = newParterre
        get_parterre(newParterre).add_capteur(self)

    def add_data(self, data):
        self.listeDonnees.append(data)

    def clear_datas(self):
        for donnee in self.get_vals():
            self.listeDonnees.remove(donnee)

#*class AlesDroits(db.Model):
#    """
#    The user idU has following rights for a Parterre idP: read, modify, suppress.
#    These rights are given by the creator of the Parterre.
#    """
#
#    Lecture     = db.Column(db.Boolean)
#    Edition     = db.Column(db.Boolean)
#    Suppression = db.Column(db.Boolean)
#    idP         = db.Column(db.Integer, db.ForeignKey("parterre.idP"), primary_key = True)
#    idU         = db.Column(db.String(50), db.ForeignKey("utilisateur.idU"), primary_key = True)
#
#    def __init__(self, Lecture, Edition, Suppression, idP, idU):
#        self.Lecture = Lecture
#        self.Edition = Edition
#        self.Suppression = Suppression
#        self.idP = idP
#        self.idU = idU
#
#    def get_id(self):
#        return (self.idP, self.idU)
#
#    def get_lecture(self):
#        return self.Lecture
#
#    def get_edition(self):
#        return self.Edition
#
#    def get_suppression(self):
#        return self.Suppression
#
#    def set_Lecture(self, NewLecture):
#        self.Lecture = NewLecture
#
#    def set_edition(self, NewEdition):
#        self.Edition = NewEdition
#
#    def set_suppression(self, NewSuppression):
#        self.Suppression = NewSuppression


class Donnee(db.Model):
    """
    Datas. Suppress a Parterre suppress the datas which are related.
    """
    idDonnee    = db.Column(db.Integer, primary_key = True)
    val         = db.Column(db.Float)
    dateRel     = db.Column(db.DateTime)
    idParterre  = db.Column(db.Integer, db.ForeignKey("parterre.idP"))

    def __init__(self, value, date, capteur, parterre):
        self.val        = value
        self.dateRel    = date
        self.idParterre = parterre
        get_capteur(capteur).add_data(self)

    def __repr__(self):
        return "<Donnee (%d) %s>" % (self.idCapt, self.dateRel, self.val)

    def get_id(self):
        return (self.dateRel, self.idCapt)

    def get_capteur(self):
        return self.idCapt

    def get_val(self):
        return self.val

    def get_date_donnee(self):
        return str(self.dateRel)

class Actions(db.Model):
    idActions=db.Column(db.Integer, primary_key= True)
    contenu=db.Column(db.String(100))

    def __init__(self,contenu,liste):
        self.contenu=contenu
        get_listeActions(liste).add_actions(self)

    def __repr__(self):
        return "%s" % (self.contenu)

    def getIdActions(self):
        return self.idActions

    def getContenu(self):
        return self.contenu


class Liste(db.Model):

    idListe=db.Column(db.Integer, primary_key=True)

    listeActions    = db.relationship("Actions",
                                      secondary = "association_liste_actions",
                                      lazy = "dynamic",
                                      backref = db.backref("actions", lazy = "dynamic"),
                                      order_by  = "desc(Actions.idActions)")

    def __repr__(self):
        return "Liste"

    def get_idListe(self):
        return self.idListe

    def get_val_actions(self):
        return self.listeActions

    def add_actions(self, data):
        self.listeActions.append(data)




def get_user(username):
    """
    recover the user place in parameter
    """
    return Utilisateur.query.filter(Utilisateur.idU==username).one()

@login_manager.user_loader
def load_user(username):
    """
    recover the user place in parameter
    """
    return Utilisateur.query.get(username)

def get_parterres():
    """
    get all the ground
    """
    return Parterre.query.all()

def get_parterre(id):
    """
    retrieve a ground from an id
    """
    return Parterre.query.get(id)

def get_typeMesures():
    """
    retrieve the types of measurement, sort by name
    """
    return TypeMesure.query.order_by(TypeMesure.nom_typeM)

def get_capteurs():
    """
    get all the sensors
    """
    return Capteur.query.all()

def get_capteur(id):
    """
    retrieve a sensor from an id
    """
    return Capteur.query.get(id)

def get_capteur_phone(num):
    """
    retrieve a sensor by phone number
    """
    return Capteur.query.filter(Capteur.numTel==num)

def get_capteurs_parterre(id):
    """
    recover a sensor from the id of a ground
    """
    return Capteur.query.filter(Capteur.parterre_id==id).all()

def get_plante(id):
    """
    recover a type of plant thanks to its id
    """
    return TypePlante.query.get(id)

def get_typeMesure(id):
    """
    recover a type of measure thanks to its id
    """
    return TypeMesure.query.get(id)

#def get_droits():
#    return AlesDroits.query.all()

def get_bac_a_sable():
    """
    recover the ground sandbox
    """
    for parterre in get_parterres():
        if parterre.get_name()=="Bac à sable":
            return parterre
    return None

def get_listeActions(id):
    """
    recover an action thanks to his id
    """
    return  Liste.query.get(id)
