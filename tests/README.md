# TESTS

Ce dossier contient les tests effectués durant les recherches préparatoires pour le projet SDN CloudStack.

## MIBs utilisées

- CISCO-VLAN-IFTABLE-RELATIONSHIP-MIB.my
- CISCO-VLAN-MEMBERSHIP-MIB.my
- CISCO-VTP-MIB.my

Toutes ces MIBs sont récuperables sur le FTP du constructeur conformément à cette fiche : https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3750/software/release/12-2_44_se/configuration/guide/scg/swmibs.pdf

## Résultats bruts

Les résultats bruts sont stockés dans des fichiers .txt, sous forme de CSV.

## Résultats mis en forme 

Les résultats sont ensuite mis en forme avec Excel.

La formule pour récupérer l'ID final est : `=DROITE(A2;NBCAR(A2) - CHERCHE(".";A2))`(a modifier au besoin)

## Réapitulatif des résultats

A l'heure actuelle, les résultats présents sont :
| Nom du fichier brut | Nom du fichier mis en forme | Description |
|---------------------|-----|------|
| walk_rtstack.txt | walk_rtstack.xlsx | Walk général effectué sur le switch RTSTACK |
| walk_rtstack2.txt | walk_rtstack2.xlsx | Second walk général effectué sur le switch RTSTACK. Contient plus d'informations |
| vlanmembership_rtstack.txt | vlanmembership_rtstack.xlsx | Subtree de la MIB CISCO-VLAN-MEMBERSHIP-MIB à partir de "ciscoVlanMembershipMIBObjects" |
| vtpvlantable_rtstack.txt | vtpvlantable_rtstack.xlsx | Subtree de la MIB CISCO-VTP-MIB à partir de "vlanInfo" |
