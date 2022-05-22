"""
Biblioteca com funções para geração de Patchs
"""


import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal
import random


def systematic(tif_path, pixelX=None, pixelY=None, tamX=None,
                    tamY=None, sobras=False):
    """
    Função para criação de patchs conforme parâmetros escolhidos pelo usuário.

    patch_generator(tif_path, pixelX=None, pixelY=None, tamX=None,
                    tamY=None)


    tif_path: Deve ser inserida uma string com o
    diretório onde a imagem raster está inserida.
    ex: '/content/crop_rapideye.tif'


    pixelX: Deve ser inserido um valor inteiro com
    a dimensão desejada para o eixo X do patch.
    ex: 300

    pixelY: Deve ser inserido um valor inteiro com
    a dimensão desejada para o eixo Y do patch.
    ex: 300

    tamX: Deve ser inserido um valor inteiro, em metros, da
    dimensão desejada para o eixo X do patch
    ex: 1500

    tamY: Deve ser inserido um valor inteiro, em metros, da
    dimensão desejada para o eixo Y do patch
    ex: 1500

    sobras: Quando True irá gerar recortes das bordas, caso estas
    apresentem dimensões inferiores às inseridas pelo usuário


    Exemplo de aplicação:
    Por exemplo, inserindo os seguintes parâmetros...

    patch_generator('/content/crop_rapideye.tif', pixelX=300, pixelY=300)

    Serão criados patches de 300x300 pixels do raster
    crop_rapideye.tif
    """

    raster = gdal.Open(tif_path)
    #Coletando os dados do raster
    gt = raster.GetGeoTransform()
    name = raster.GetDescription()
    name = name.split('.')[-2]

    # Separando os valores da lista gt
    img_xmin = gt[0]
    img_ymax = gt[3]
    res = gt[1]

    # Verificandoo tamanho da imagem nos eixos x e y.
    # n_pixelsx é o numero de pixels na dimensão x
    # img_xlen é tamanho da imagem em metros na dimensão x 

    n_pixelsx = raster.RasterXSize
    n_pixelsy = raster.RasterYSize

    img_xlen = res * n_pixelsx
    img_ylen = res * n_pixelsy


    #Delimitando o tamanho do patch
    #xsize e ysize é o tamanho do patch em metros.

    #Caso o usuário insira o valor das dimensões do patch em pixels
    if pixelX != None and pixelY != None:
        # tamanho do patch em metros
        patch_xlen = pixelX * res 
        patch_ylen = pixelY * res
        print(f'Tamanho do patch: {patch_ylen}m x {patch_ylen}m')

    #Caso o usuário insira o valor das dimensões do patch em metros
    elif  tamX != None and tamY != None:
        patch_xlen = tamX
        patch_ylen = tamY

    xdiv = img_xlen//patch_xlen
    ydiv = img_ylen//patch_ylen

    total_patches= xdiv*ydiv
    print(f'Número total de patches ({pixelX}x{pixelY}) criados: {total_patches}')

    # Testando se o tamanho da imagem é proporcional ao tamanho do patch
    # nas duas dimensões
    if img_xlen % patch_xlen != 0 or img_ylen % patch_ylen !=0:
       print(f'O tamanho da imagem não é múltiplo do tamanho do patch.\n')
       
       if sobras:
         if img_xlen % patch_xlen != 0:
            xdiv += 1
         elif img_ylen % patch_ylen !=0:
            ydiv += 1
         t_patches= xdiv*ydiv
         print(f'Número total de patches a serem criados (+ sobras): {total_patches}')

    xsteps = [img_xmin + patch_xlen*i for i in range(int(xdiv)+1)]
    ysteps = [img_ymax - patch_ylen*i for i in range(int(ydiv)+1)]

    resp = input(f'Você gostaria de criar {total_patches} patches? (S/N)')
    if resp.upper() == 'S':
        id = 1
        for i in range(int(xdiv)):
            for j in range(int(ydiv)):
                xmin = xsteps[i]
                xmax = xsteps[i+1]
                ymax = ysteps[j]
                ymin = ysteps[j+1]

                #print('xmin:'+str(xmin))
                #print('xmin:'+str(xmax))
                #print('ymin:'+str(ymin))
                #print('ymin:'+str(ymax))
                #print('\n')
                gdal.Warp(name + '_' + 'p' + str(id) +'.tif', raster, outputBounds = (xmin, ymin, xmax, ymax), dstNodata = -9999)
                id += 1
        print(f'{total_patches} criados!')
    elif resp.upper() == 'N':
        print('Programa finalizado, você optou por não criar nenhum patch.')
        print('-' * 100)



if __name__ == "__main__":
    import sys
    print(normal(
            float(sys.argv[1]), float(sys.argv[2]),
            float(sys.argv[3]), float(sys.argv[4])
          )
    )


def point_intersection(x1,y1,x2,y2,pixelX,pixelY):
  return x2 <= x1 <= x2 + pixelX and y2 <= y1 <= y2 + pixelY


def patch_intersection(x1,y1,x2,y2,pixelX,pixelY):
  return (point_intersection(x1,y1,x2,y2,pixelX,pixelY) or 
   point_intersection(x1 + pixelX ,y1,x2,y2,pixelX,pixelY) or
   point_intersection(x1,y1 + pixelY,x2,y2,pixelX,pixelY) or
   point_intersection(x1 + pixelX,y1 + pixelY,x2,y2,pixelX,pixelY))


def rand(tif_path, pixelX=None, pixelY=None, tamX=None,
                    tamY=None, t=1000):
    """
    DOCSTRING
    """
    raster = gdal.Open(tif_path)
    #Coletando os dados do raster
    gt = raster.GetGeoTransform()
    print(gt)

    name = raster.GetDescription()
    name = name.split('.')[-2]
    # Separando os valores da lista gt
    img_xmin = gt[0]
    img_ymax = gt[3]
    res = gt[1]

    if tamX != None and tamY != None:
        pixelX = tamX // res
        pixelY = tamY // res

    n_pixelsx = raster.RasterXSize
    n_pixelsy = raster.RasterYSize

    img_xlen = res * n_pixelsx
    img_ylen = res * n_pixelsy

    # limites da geração aleatória de pontos
    img_limx = n_pixelsx - pixelX
    img_limy = n_pixelsy  - pixelY

    # Parâmetros iniciais para cálculo das posições aleatórias
    iteracoes=0
    indice = 0
    tentativas = 0
    vetor = []  

    while True:
      # Inicialização dos parâmetros
      any_intersection = False 
      iteracoes +=1

      x = random.randrange(0,img_limx)
      y = random.randrange(0,img_limy)
      
      xmin = img_xmin + (x * res)
      xmax = xmin + pixelX*res
      ymax = img_ymax - (y * res)
      ymin = img_ymax - (y + pixelY)*res
              
      for old_x,old_y in vetor:
        if patch_intersection(old_x,old_y,x,y, pixelX, pixelY):
          any_intersection = True

      if not any_intersection:
        gdal.Warp(name + '_' + 'rp' + str(indice) +'.tif', raster, outputBounds = (xmin, ymin, xmax, ymax), dstNodata = -9999)
        vetor.append((x,y))
        indice +=1
        tentativas = 0
      else:
        tentativas +=1
      
      if tentativas >= t:
          print(f'Número de tentativas atingido {t} sem resolução.')
          print(f'Número de patches criados: {indice}')
          print(f'Iterações = {iteracoes}')
          break
          

def rand_overlap(tif_path, pixelX=None, pixelY=None,t=2000, tamX=None,
                    tamY=None, npatch=None):
    """
    DOCSTRING
    """
    raster = gdal.Open(tif_path)
    #Coletando os dados do raster
    gt = raster.GetGeoTransform()
    print(gt)

    name = raster.GetDescription()
    name = name.split('.')[-2]
    # Separando os valores da lista gt
    img_xmin = gt[0] #Coordenada x do pixel do canto superior esquerdo
    img_ymax = gt[3] #Coordenada y do pixel do canto superior esquerdo
    res = gt[1] #Resolução do pixel ao longo do eixo x

    if tamX != None and tamY != None:
        pixelX = tamX // res
        pixelY = tamY // res

    n_pixelsx = raster.RasterXSize
    n_pixelsy = raster.RasterYSize

    img_xlen = res * n_pixelsx
    img_ylen = res * n_pixelsy

    # limites da geração aleatória de pontos
    img_limx = n_pixelsx - pixelX
    img_limy = n_pixelsy  - pixelY

    # Parâmetros iniciais para cálculo das posições aleatórias
    iteracoes=0
    indice = 1
    vetor = []  

    while True:
        # Inicialização dos parâmetros
        any_intersection = False 
        iteracoes +=1

        x = random.randrange(0,img_limx)
        y = random.randrange(0,img_limy)

        xmin = img_xmin + (x * res)
        xmax = xmin + pixelX*res
        ymax = img_ymax - (y * res)
        ymin = img_ymax - (y + pixelY)*res
              
    
        gdal.Warp(name + '_' + 'rp' + str(indice) +'.tif', raster, outputBounds = (xmin, ymin, xmax, ymax), dstNodata = -9999)
        vetor.append((x,y))
        indice +=1
      
        if indice > npatch:
            break
          