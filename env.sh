read -p "Voulez vous (re)créer le virtualenv ?[y/n]" reponse
if echo "$reponse" | grep -iq "^y" ;then
    rm -rf venv
    virtualenv -p python3 venv
fi

echo

source venv/bin/activate
read -p "Voulez vous (re)installer les modules ?[y/n]" reponse
if echo "$reponse" | grep -iq "^y" ;then
  pip install -r NotreApli/Web/requirements.txt
fi

echo

read -p "Voulez vous (re)charger la base de données ?[y/n]" reponse
if echo "$reponse" | grep -iq "^y" ;then
  rm NotreApli/Web/tuto.db
  ./NotreApli/Web/manage.py loaddb
fi

echo

read -p "Voulez vous démarer le serveur ?[y/n]" reponse
if echo "$reponse" | grep -iq "^y" ;then
  firefox localhost:5000
  ./NotreApli/Web/manage.py runserver
fi

echo
