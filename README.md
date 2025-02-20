# 📘 Projet : EpicEvent - CRM pour la Gestion d'Événements

## 📌 **Présentation du Projet**
Epic Events est une entreprise spécialisée dans l'organisation d'événements. Ce projet CRM a pour but de **faciliter la gestion des clients, contrats et événements**, tout en assurant un contrôle des accès par rôles.

L'architecture du projet repose sur **Python 3.9+**, **SQLAlchemy** pour la gestion de la base de données, et **Typer** pour l'interface en ligne de commande (CLI). 

Le projet est divisé en trois modules principaux :
- **Gestion des utilisateurs et permissions**
- **Gestion des clients et contrats**
- **Organisation des événements**

---

## 📌 **Installation et Configuration**

### ✅ **1. Cloner le Dépôt**
Si le projet est sur GitHub :
```sh
git clone https://github.com/ton-repo/epicevent.git
cd epicevent
```

Si tu n’utilises pas Git, télécharge l’archive et extraits les fichiers.

### ✅ **2. Créer et Activer un Environnement Virtuel**
**Sous Windows :**
```sh
python -m venv venv
venv\Scripts\activate
```

**Sous macOS/Linux :**
```sh
python3 -m venv venv
source venv/bin/activate
```

### ✅ **3. Installer les Dépendances**
```sh
pip install -r requirements.txt
```

### ✅ **4. Initialiser la Base de Données**
```sh
python main.py db init
python main.py db migrate
python main.py db upgrade
```

### ✅ **5. Lancer l’Application**
```sh
python main.py
```

### ✅ **6. Exécuter les Tests Unitaires**
```sh
pytest -v
```

---

## 📌 **Commandes Disponibles**

### 🔹 **Gestion des Utilisateurs**
```sh
python main.py user create --username admin --email admin@example.com --password admin123 --role GESTION
```

### 🔹 **Gestion des Clients**
```sh
python main.py client create --first-name John --last-name Doe --email john@example.com --phone 123456789 --company-name Startup
```

### 🔹 **Gestion des Contrats**
```sh
python main.py contract create --client-id 1 --total-amount 5000 --remaining-amount 2500
```

### 🔹 **Gestion des Événements**
```sh
python main.py event create --client-id 1 --contract-id 1 --name "Réunion annuelle" --start-date "2024-06-01_10:00:00" --end-date "2024-06-01_12:00:00" --location "Paris"
```

---

## 📌 **Bonnes Pratiques et Sécurité**
- **Validation stricte des entrées utilisateur** pour éviter les injections SQL.
- **Gestion des accès basée sur les rôles** pour éviter les fuites de données.
- **Journaux d’erreurs avec Sentry** pour détecter et résoudre les anomalies.
- **Architecture modulaire** pour faciliter la maintenance et l’évolutivité.

---

## 📌 **Débogage et Solutions aux Problèmes Courants**
### 🔹 **Erreur : `ModuleNotFoundError: No module named 'sqlalchemy'`**
Solution :
```sh
pip install SQLAlchemy
```

### 🔹 **Erreur : `pytest` ne trouve pas les tests**
Solution :
```sh
python -m pytest
```

### 🔹 **Erreur : `sqlite3.OperationalError: unable to open database file`**
Solution :
- Assure-toi que **la base de données a été initialisée** (`python main.py db init`).
- Vérifie que l’application a les **droits d’accès** au fichier `database.db`.

---

## 🎯 **Conclusion**
Avec ce guide, tu peux maintenant **installer, configurer et exécuter** EpicEvent CRM efficacement. 🎯

📌 **Commande finale pour tout tester :**
```sh
pytest -v
```

Bonne utilisation du CRM ! 🚀

