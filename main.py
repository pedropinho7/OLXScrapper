import pandas
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import ArcGIS
import folium

nom = ArcGIS()

def Buscar_dados_OLX(paginas, categoria, query):
    if categoria.lower() == "all":
        categoria = "ads"
    lista_json = []
    print("Ligação iniciada ao OLX.")
    for nr_pagina in range(paginas):
        url = f"https://www.olx.pt/d/{categoria}/q-{query}"
        if nr_pagina != 0:
            url = f"https://www.olx.pt/{categoria}/q-{query}?page={str(nr_pagina)}"
        page = requests.get(url=url)
        soup = BeautifulSoup(page.content, features="html.parser")
        anuncios = soup.findAll('tr', {"class": "wrap"})
        #with open("AnuncioBody.txt", 'a+') as file:
        #    file.write(str(anuncios[0]))
        for anuncio in anuncios:
            titulo = anuncio.find_all("a")[1].contents[1].text.strip()
            #print(titulo)
            if query.lower() in titulo.lower():
                preco = anuncio.find_all("p", {"class": "price"})[
                    0].text.strip()
                data = anuncio.find_all("p", {"class": "lheight16"})[
                    1].contents[3].text.strip()
                localizacao = anuncio.find_all("p", {"class": "lheight16"})[
                    1].contents[1].text.strip()
                url_anuncio = anuncio.find("a")["href"]
                if anuncio.find("img") is None:
                    url_imagem = "None"
                else:
                    url_imagem = anuncio.find("img")["src"]
                # re.match(r".*([1-2][0-2]{3})", titulo)
                # ano = int(re.findall('(\d{4})', titulo)[0])
                json = {"Data": data,
                        "Título": titulo,
                        "Preço": preco,
                        "Localização": localizacao,
                        "Link": url_anuncio,
                        "Img Link": url_imagem,
                        # "ano": ano,
                        }
                lista_json.append(json)
            else:
                pass
    df_anuncios = pandas.DataFrame(lista_json)
    print("Ligação ao OLX terminada.")      
    return df_anuncios

def Guardar_Dados_Mapa(dataFrame):
    print("A criar mapa.")
    map = folium.Map(location=[41.033890, -8.583272], zoom_start = 6, tiles="Stamen Terrain")
    fg = folium.FeatureGroup(name="Mapa de pesquisa")
    lat = list(dataFrame["Latitude"])
    lon = list(dataFrame["Longitude"])
    url = list(dataFrame["Link"])
    img_url = list(dataFrame["Img Link"])
    titulo = list(dataFrame["Título"])
    date = list(dataFrame["Data"])
    price = list(dataFrame["Preço"])
    for lt, ln, link, img_link, title, dt, price in zip(lat, lon, url, img_url, titulo, date, price):
        html = f'''<p>{title}<p/>
                <a href="{link}" target="_blank">Link para anúncio<a/>
                <p>Data: {dt} </p>
                <p>Preço: {price} </p>
                '''
        iframe = folium.IFrame(html, width=300, height=250)
        fg.add_child(folium.Marker(location=[lt,ln], popup=folium.Popup(iframe), icon = folium.Icon(color="blue")))

    map.add_child(fg)
    map.save("QueryMapResults.html")
    print("Mapa criado.")

def Guardar_Dados_Excel(dataframe):
    print("A guardar dados no Excel")
    pandas.DataFrame(dataframe).to_excel("macbook1-M1-query.xlsx")
    print("Dados guardados no Excel.")
    
def Converter_Localizacao_Para_Coordenadas(dataframe):
    print("A iniciar conversão de localidades para coordenadas.")
    dataframe["Coordenadas"] = dataframe["Localização"].apply(nom.geocode)
    dataframe["Latitude"] = dataframe["Coordenadas"].apply(lambda x: x.latitude if x.latitude != None else None)
    dataframe["Longitude"] = dataframe["Coordenadas"].apply(lambda x: x.longitude if x.longitude != None else None)
    print("Conversão concluída.")
    return dataframe



lista_de_anuncios = Buscar_dados_OLX(paginas=15, categoria="tecnologia-e-informatica/computadores-informatica", query="Macbook")
#################################################################################
#                              Categorias JÁ TESTADAS A FUNCIONAR               #
# tecnologia-e-informatica                                                      #
# 'all' para todos                                                              #
#                   CATEGORIAS POR TESTAR, MAS DEVEM FUNCIONAR ;)               #
# lazer                                                                         #
# telemoveis-e-tablets                                                          #
# bebes-criancas                                                                #
# animais                                                                       #
# desporto-e-lazer                                                              #
# moda                                                                          #
# moveis-casa-e-jardim                                                          #
# carros-motos-e-barcos      carros     motociclos-scooters                     #
#                                                                               #  
#                                                                               #
#                                                                               # 
#                                                                               # 
#################################################################################
Guardar_Dados_Excel(lista_de_anuncios)
lista_com_coordenadas = Converter_Localizacao_Para_Coordenadas(lista_de_anuncios)
Guardar_Dados_Excel(lista_com_coordenadas)
Guardar_Dados_Mapa(lista_com_coordenadas)