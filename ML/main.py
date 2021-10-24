
import pandas as pd
import pdf2 as pdf
import docx_docs as docs
import tf_fio
import os

# pdf_name2 = os.curdir + '/files/documents_files_1135_02032020_PR-49_20_Ovchinskii_VA_Gosydarstvennaya_inspekciya_po_kontrolu_za_ispolzovaniem_obektov_nedvijimosti_goroda_Moskvi.pdf'
# pdf_name = os.curdir + '/files/documents_docs_06102016_64-02-1201_16_Sobyanin_SS_Pechatnikov_LM (1).pdf'
# doc_name = os.curdir + '/files/documents_files_2705_NASAITGBY2020.docx'




#Передаем путь для изображения
def recogn_image(file_name, dpi = 300):
    """Метод для распознавания изображений"""

    extractor_im = pdf.PDFExtractor3(file_name, dpi = dpi)
    extractor_im.image_list()
    df_recogn = extractor_im.parse_page()
    model = tf_fio.Predictor()
    l = list(df_recogn.text)
    predict = model.bst_predict(l)
    df_recogn['flag'] = pd.Series(predict)
    hide = pdf.Hide_PD(extractor_im.pagelist)
    hide.fill_image(df_recogn[df_recogn.flag == 1])
    print('Output file {0}'.format(extractor_im.output_fname))
    return extractor_im.output_fname


#Передаем путь для docx
def recogn_doc(file_name):
    """Метод для распознавания docx"""

    doc = docs.Docs(file_name)
    doc.recogn_doc()
    report = doc.report()
    print('Всего: {2}, Найдено персональных данных: {1}. Найдено не персональных данных: {0}'
          .format(report[2], report[1], report[0]))
    print('Output file {0}'.format(doc.output_fname))
    return doc.output_fname


#Передаем путь для pdf
def recogn_pdf(file_name, dpi = 300):
    """Метод для распознавания pdf"""

    extractor = pdf.PDFExtractor3(file_name, dpi = dpi)
    extractor.convert_to_jpg()
    df_recogn = extractor.parse_page()
    model = tf_fio.Predictor()
    l = list(df_recogn.text)
    predict = model.bst_predict(l)
    df_recogn['flag'] = pd.Series(predict)
    df_recogn.to_csv(os.curdir + '/files/recogn.csv')
    hide = pdf.Hide_PD(extractor.pagelist)
    hide.fill_image(df_recogn[df_recogn.flag == 1])
    extractor.img2pdf()
    report = extractor.report()

    print('Всего: {2}, Найдено персональных данных: {1}. Найдено не персональных данных: {0}'
          .format(report[2], report[1], report[0]))
    print('Output file {0}'.format(extractor.output_fname))
    extractor.delete_temp_files()

    return extractor.output_fname



# recogn_pdf(pdf_name)
recogn_doc(doc_name)
# recogn_image(os.curdir + '/files/doc.png')

# for root, dirs, files in os.walk(os.curdir+ '/files/', topdown = False):
#    for name in files:
#       f = os.path.join(root, name)
#       if f.split('.')[-1]=='pdf':
#           recogn_pdf(os.curdir+f[1:])
#           print(f)
