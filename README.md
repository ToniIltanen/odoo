# Odoonn asennus

## Docker kontit

kansion juuressa aja seuraava komento:
```
docker-compose up -d
```

Paketti asentaa Odon:n, sen tarvitseman postgresql:n ja keycloakin

Odoo löytyy osoitteesta: http://localhost:8059
Keycloak löytyy osoitteesta http://localhost:8080

## SSO:n asentaminen
Kirjaudu admin tunnuksilla ODOO:seen. 
Vasemmasta yläkulmasta avaa **Sovellukset**

Asenna seuraavat sovellukset, jos eivät vielä ole asennettuna:
![alt text](<Screenshot 2026-10-04 at 17.01.15.png>)

Asennuksen jälkeen valitse vasemmasta yläkulmasta **Asetukset** ja valitse OAUTH-asetukset painamalla **OAuth-palveluntarjoajat**:
![alt text](<Screenshot 2026-10-04 at 17.04.14.png>)

### Uuden integraation luominen

1. valitse vasemmasta yläkulmasta **Uusi**
![alt text](<Screenshot 2026-10-04 at 17.04.27.png>)
2. Syötä arvot:
![alt text](<Screenshot 2026-10-04 at 17.04.34.png>)

Mikäli keycloakin asetukset ovat erilaiset, käytä asennetun keycloakin oikeita osoitteita

## Keycloak

Keycloak löytyy osoitteesta http://localhost:8080

Kirjaudu admin tunnuksilla sisään, ja luo uusi Realm **Create realm** painikkeesta, anna realmin nimeksi  **odoo** (huom. kaikki pienellä). Mikäli Create Realm ei näy, valitse vasemmasta valikosta **Manage Realms**

![alt text](<Screenshot 2026-10-04 at 17.09.19.png>)

Valitse **Resource File** Browse painikkeesta, ja anna anna tiedostoksi tässä kansiossa oleva **realm-export.json** ja paina **Create**
![alt text](<Screenshot 2026-10-04 at 17.11.37.png>)

Clients listalta tulisi nyt löytyä odoo-niminen Client:
![alt text](<Screenshot 2026-10-04 at 17.12.04.png>)

Valitse vasemmasta valikosta **Realm Settings** ja anna osoite jossa keycloak kuuntelee (ja joka on sama osoite, jota Odoo kutsuu):

![alt text](<Screenshot 2026-10-04 at 17.13.08.png>)

##Käyttäjän lisääminen:

1. Valitse vasemmasta valikosta Keycloakissa **Users**:
![alt text](<Screenshot 2026-10-04 at 17.14.32.png>)

2. Valitse **Add User**
3. Täytä tarvittavat kentät (huom. Täppää Email Verified päälle):
![alt text](<Screenshot 2026-10-04 at 17.16.10.png>)
4. Valitse **Join Groups** ja lisää henkilö joko User ryhmään tai Admin ryhmään:
![alt text](<Screenshot 2026-10-04 at 17.16.20.png>)
5. Tallenna käyttäjä painamalla **Create** Painiketta