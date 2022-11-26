## Chiffrement

# Question 1 : Quelle est le nom de l'algorithme de chiffrement? Est-il robuste et pourquoi ?

> Chiffrement par flux avec une porte XOR
> non pas robuste car onpeut trouver la clef facilement si on a des backup de certains fichiers qui ont été chiffrés avec

## Génération des secrets

# Question 2 : Pourquoi ne pas hacher le sel et la clef directement ? Et avec un hmac ?

> 

## Setup

# Question 3 : Pourquoi il est préférable de vérifier qu'un fichier token.bin n'est pas déjà présent ?

## Vérifier et utiliser la clef

# Question 4 : Comment vérifier que la clef est la bonne ?

> La clef est correct si la combinaison de la clef et du sel donne le même hash que le hash du fichier token.bin 