# TD Ransomware

## 1. Description du travail

Ce devoir a pour objectif de créer un ransomware chiffrant les fichiers d'un ordinateur et envoyant une clé de déchiffrement à un serveur distant.

Afin de ne pas endommager d'ordinateur le ransomware sera exécuter dans un environnement Docker. Les 2 conteneurs seront lancés sur une même machine.

## 2.Installation et lancement

### 2.1. Prérequis

Installation de la commande sudo :
Pour Debian/Ubuntu :

```bash
apt install sudo
```

Installation de Docker :
Vous pouvez suivre les instruction sur : https://docs.docker.com/engine/install/ 

### 2.2. Création des conteneurs docker

Pour créer les conteneurs, il faut se placer dans le dossier du projet puis exécuter la commande suivante :
```bash
sudo chmod +x build.sh && sudo ./build.sh
```

### 2.3. Serveur CNC

Une fois les conteneurs crées, avant d'exécuter le ransomware, il faut lancer le serveur CNC. Pour le lancer, il faut se rendre dans le dossier projet et executer cette comamnde :
```bash
sudo chmod +x run_cnc.sh && sudo ./run_cnc.sh
```

### 2.4. Client

Pour lancer le ransomware, il faut se placer dans le dossier du projet et exécuter la commande suivante :
```bash
sudo chmod +x run_ransomware.sh && sudo ./run_ransomware.sh
```

 Pour seulement lancer l'environnement Docker (sans lancer le ransomware), vous pouvez exécuter la commande suivante :
 ```bash
 sudo chmod +x exec_target.sh && sudo ./exec_target.sh
 ```
 Ensuite pour exécuter le ransomware vous pouvez exécuter cette commande :
 ```bash
 cd /root/ransomware && python3 ransomware.py
 ```
 
 ### 3. Fonctionnement
 
### 3.1. Fonctionnement général du ransomware

Quand le ransomware est lancé, il chiffre les fichiers txt du dossier `/root` puis envoie la clé de déchiffrement au serveur CNC et enregistre le salt et le token sous forme binaire dans le dossier `token_data` sur la machine.

Quand le chiffrement est fini, le ransomware affiche un message sur le terminal avec le token.

### 3.2. Récupération des fichiers

Pour récupérer les fichiers, il faut récupérer la clé. Pour cela, il faut aller du côté du serveur CNC.

1ère manière de récupérer la clé :
Regarder directement dans les logs du serveur CNC puis copier la clé sous forme base64.

2ème manière de récupérer la clé :
Se rendre dans le dossier `cnc_data` de la machine et récupérer la clé sous forme binaire.Une fois dans le dossier `cnc_data`, elle est contenu dans le dossier ayant pour nom le token de la victime et se trouve dans le fichier 'key.bin'. Afin de déchiffrer les fichiers texte, il vous faudra simplement reconvertir la clé binaire en base64.

Une fois la clé récupéré dans le cas où vous aviez exécuter le script `exec_target.sh`, il faut se placer dans le dossier `/root/ransomware` et exécuter la commande suivante :
```bash
python3 ransomware.py --decrypt
```
Un formulaire va alors s'afficher. Il faut alors entrer la clé de déchiffrement en base64 récupérée sur le CNC et appuyer sur la touche `Entrée`.

## 4. Réponses aux questions

# Question 1 : Quelle est le nom de l'algorithme de chiffrement? Est-il robuste et pourquoi ?

> Chiffrement par flux avec une porte XOR
> non pas robuste car onpeut trouver la clef facilement si on a des backup de certains fichiers qui ont été chiffrés avec


# Question 2 : Pourquoi ne pas hacher le sel et la clef directement ? Et avec un hmac ?

> 


# Question 3 : Pourquoi il est préférable de vérifier qu'un fichier token.bin n'est pas déjà présent ?


# Question 4 : Comment vérifier que la clef est la bonne ?

> La clef est correct si la combinaison de la clef et du sel donne le même hash que le hash du fichier token.bin 
