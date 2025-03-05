## 📚 **EpicEvent - CRM pour la Gestion d'Événements**  

### 🎯 **Présentation du Projet**  
EpicEvent est un CRM conçu pour **gérer les clients, contrats et événements**, tout en assurant une **gestion stricte des permissions** selon les rôles utilisateurs.  

🔹 **Technologies utilisées** :  
- **Python 3.9+**  
- **SQLAlchemy** *(ORM pour base de données)*  
- **Typer** *(Interface CLI)*  
- **SQLite** *(Base de données locale)*  
- **pytest** *(Tests unitaires)*  
- **Sentry** *(Gestion des erreurs et logs)*  

---

## ⚡ **Installation et Configuration**  

### ✅ **1. Cloner le Dépôt**  
Si le projet est sur GitHub :  
```sh
git clone https://github.com/antogro/P12-EpicEvents.git
cd EpicEvents
```  

Si tu n’utilises pas Git, télécharge l’archive et extraits les fichiers.

### ✅ **2. Créer et Activer un Environnement Virtuel**  
**Sous Windows :**  
```sh
python -m venv .venv
.venv\Scripts\activate
```  

**Sous macOS/Linux :**  
```sh
python3 -m venv .venv
source venv/bin/activate
```  

### ✅ **3. Installer les Dépendances**  
```sh
pip install -r requirements.txt
```  

### ✅ **4. Configuration du Projet**  
Créer un fichier **`.env`** à la racine du projet et ajouter les variables nécessaires :  
```ini
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///epic_event.db
TOKEN_EXPIRATION=3600
```  

### ✅ **5. Initialiser la Base de Données et l'Administrateur Gestion**
```sh
python database.py
python create_admin.py
```  

### ✅ **6. Exécuter les Tests Unitaires**  
```sh
pytest -v
```  

---

## 🔐 **Gestion des Utilisateurs et Permissions**  

EpicEvent applique un **contrôle d'accès strict** basé sur trois rôles :  
| Rôle       | Droits |
|------------|------------------------------------------------|
| **GESTION** | Gestion des utilisateurs, des contrats et des événements |
| **COMMERCIAL** | Création et gestion des clients, contrats et événements |
| **SUPPORT** | Gestion des événements qui leur sont attribués |

📌 **Principaux droits par rôle** :  
✅ **GESTION** : Peut créer/modifier/supprimer tout utilisateur, contrat ou événement.  
✅ **COMMERCIAL** : Peut gérer ses propres clients et contrats, créer des événements.  
✅ **SUPPORT** : Peut modifier les événements qui lui sont attribués.  

---

## 🚀 **Exemples d'Utilisation**  

### 🔹 **Connexion (Authentification)**
```sh
python main.py auth login --username admin --password AdminSecure123!
```  

### 🔹 **Gestion des Utilisateurs**  
Créer un utilisateur (Equipe Gestion):  
```sh
python main.py user create --username testuser --email testuser@example.com --password password --role GESTION
```  

Lister les utilisateurs (Toutes les Equipes):  
```sh
python main.py user report
```  

### 🔹 **Gestion des Clients**  
Créer un client (Equipe Commerciale):  
```sh
python main.py client create --first-name Alice --last-name Dupont --email alice@example.com --phone 0601020304 --company-name "Startup Inc."
```  

### 🔹 **Gestion des Contrats**
Créer un contrat (Equipe Gestion):
```sh
python main.py contract create --client-id 1 --commercial-id 3 --total-amount 3000 --remaining-amount 3000
```

Signer un contrat (Equipe Commerciale/Gestion):  
```sh
python main.py contract sign --id 4
```  

### 🔹 **Gestion des Événements**  
Créer un événement (Equipe Gestion):  
```sh
python main.py event create --client-id 1 --contract-id 1 --name Conférence annuelle --start-date 2029-09-15_09:00:00 --end-date 2029-09-15_12:00:00 --location Paris --attendees 50 --notes Événement VIP
```  


---

## 🔧 **Dépannage - Problèmes Courants et Solutions**  

### ❌ `ModuleNotFoundError: No module named 'sqlalchemy'`  
✅ **Solution :** Installer SQLAlchemy  
```sh
pip install SQLAlchemy
```  

### ❌ `pytest` ne trouve pas les tests  
✅ **Solution :**  
```sh
python -m pytest
```  

---

## 🎯 **Conclusion**  
Avec ce guide, tu peux maintenant **installer, configurer et exécuter** EpicEvent CRM efficacement.  
