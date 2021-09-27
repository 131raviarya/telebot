from PIL import Image, ImageFont, ImageDraw
import datetime
import pytz


IST = pytz.timezone('Asia/Kolkata')


def cropImg(name):
    im = Image.open(name)
    im1 = im.crop((729, 577, 1399, 861))
    im1.save(name)


def makeImage(c, batch):
    # a= [' ','CPH1 15:45-17:45', 'PBK 15:45-17:45',' ','MNJ 15:45-17:45', ' ', ' ']
    # b= [' ','MNJ 18:00-20:00', 'CPH1 18:00-20:00', ' ', 'PBK 18:00-20:00',' ', ' ']
    #from PIL import Image, ImageFont, ImageDraw
    my_image = Image.open("f_Schh.jpg")
    title_font = ImageFont.truetype('Candrb__.ttf', 45)
    image_editable = ImageDraw.Draw(my_image)

    y = 0
    for i in c:
        y_cor = 458 + (y * 182)
        x = 0
        for j in i:
            x_cor = 120 + (x * 259)

            # if j.startswith('C'): j = 'Chemistry\n' + j[::-1][:11][::-1]
            # if j.startswith('P'): j = 'Physics\n' + j[::-1][:11][::-1]
            # if j.startswith('M'): j = 'Mathematics\n' + j[::-1][:11][::-1]
            title_text = j.replace(' ', '\n')
            if y==0: image_editable.text((x_cor, y_cor), title_text, (256, 256, 256), font=title_font)
            else : image_editable.text((x_cor, y_cor), title_text, (218, 0, 0), font=title_font)
            x = x + 1
        y = y + 1

    title_font = ImageFont.truetype('cambria.ttc', 48)
    image_editable = ImageDraw.Draw(my_image)
    image_editable.text((1067, 276), batch, (0, 0, 0), font=title_font)
    title_font = ImageFont.truetype('cambria.ttc', 30)
    image_editable.text((1400, 1433), "Updated :"+str(str(datetime.datetime.now(IST))[:19]), (0, 0, 0), font=title_font)
    my_image.save('Schedule.jpg')
    #my_image.show()

def imageMaker(lst, batch):
  from selenium import webdriver
  from selenium.webdriver.chrome.options import Options
  import os

  data= lst
  data1=data[0]
  data2=data[1:]
  print('reached')
  lst1=['<th>'+i+'</th>' for i in data1]
  lst2=[['<td>'+data2[j][i]+'</td>' for i in range(7)] for j in range(4) ]
  lst3=['x2','x3','x4','x5']
  # print(lst1)
  # print(lst2, len(lst2))
  time="Updated :"+str(str(datetime.datetime.now(IST))[:19])
  batchcode=batch
  with open('table.html','r+') as file:
      x=file.read()
      x=x.replace('batch',batchcode)
      x=x.replace('x1', ''.join(lst1))
      x=x.replace('update',time)
      for i in range(4):
          x=x.replace(lst3[i],''.join(lst2[i]))
      # print(x)
  with open('table2.html','w') as file2:
    file2.write(x)

  print('html created')
  chrome_options = Options()
  WINDOW_SIZE = "1920,1080"
  chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
  chrome_options.add_argument("--headless")
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=chrome_options)
  path =  os.path.abspath('table2.html')
  print(path)

  driver.get(r"file:///"+path)


  elem=driver.find_element_by_class_name('container')
  elem.screenshot('Schedule.png')
  driver.quit()