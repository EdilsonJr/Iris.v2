from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.views import generic
from django.core.files.storage import FileSystemStorage
import os
from django.urls import reverse
import json
import analyzer.text_preprocessing_functions as text_preprocessing
import pickle
from pathlib import Path
import shutil
from django.template import loader
from .models import Data, Analyzer

import numpy as np


def clear_temp_dir():
    folder = 'temp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def download_file(request):
    user_id = request.session['user_key']
    # file_path = os.path.join("uploads", "zips", "{}_user_zip".format(user_id), "resumes{}.zip".format(user_id))
    file_path = os.path.join("temp", f"{user_id}_results", f"resumes_{user_id}.zip")

    # zipped_file = open(file_path, "wb")
    # to_file = file
    # zipped_file.write(to_file)
    # zipped_file.close()

    filename = "{}_download.zip".format(user_id)
    fl = open(file_path, 'rb')
    return FileResponse(fl, as_attachment=True, filename=filename)


class AiAnalyzer(generic.DetailView):
    model = Data
    template_name = 'analyzer/analyzer.html'
    context_object_name = 'obj_model'

    def get(self, request):
        # print('TESTE DE SESSION: {}'.format(request.session['user_key']))

        return render(request, self.template_name, {})

    def get_context_data(self, **kwargs):
        context = super(AiAnalyzer, self).get_context_data(**kwargs)
        context['models'] = Data.objects.all()
        context['page_title'] = 'Analyzer'

        return context


def analyzer_store(request):
    """
    Recebendo os dados
    """
    user_id = request.session['user_key']
    key_word = request.POST['key_word']

    try:
        data = request.FILES['file']
        fs = FileSystemStorage('temp')
        filename = fs.save(data.name, data)  # "data.name" pode nao funcionar
        with open("temp/{}".format(data.name), 'rb') as file:
            binary = file.read()
    except BaseException as err:
        print('ERRO: {}'.format(err))
        data = False
        binary = None

    """
    Salvando os dados
    """
    # analyser = Data.objects.get(user_key=user_key)
    try:
        data_obj = Data.objects.get(user_key=user_id)
    except Data.DoesNotExist:
        data_obj = Data()

    data_obj.key_word = key_word
    data_obj.file = binary
    data_obj.user_key = user_id
    data_obj.save()

    """
    Clear 'temp' dir
    """
    clear_temp_dir()
    analyzer(request)
    # return HttpResponseRedirect(reverse('main:analyzer', args=['ResumeAnalyzer']))
    return HttpResponseRedirect(reverse('result'))


def analyzer(request):
    print("Starting prediction function...")
    user_id = request.session['user_key']
    try:
        # Gets the trained AI component
        model = Analyzer.objects.get(name='ResumeAnalyzerNB')
        # Gets the especific Data from the especific user  
        user_data = Data.objects.get(user_key=user_id)
    except BaseException as err:
        model = None
        print(f'Erro: {err}')
    except Data.DoesNotExist as data_unexist:
        user_data = None
        raise ValueError(f'Erro: {data_unexist}')

    print("Loading the model from pickle...")
    ai = pickle.loads(model.model)
    word_vec = pickle.loads(model.word_vec)
    le = pickle.loads(model.label_encoder)

    # Creating path to store the data to predict
    dir_name = Path(os.path.join("temp", "{}_to_predict".format(user_data.id)))
    dir_name.mkdir(parents=True, exist_ok=True)

    # Getting the path containing data to predict
    file_path = os.path.join("temp", "{}_to_predict".format(user_data.id), "resumes_{}.zip".format(user_data.id))

    # Writing the binary zipped user file to a zipfile
    zipped_file = open(file_path, "wb+")
    zipped_file.write(user_data.file)
    zipped_file.close()

    list_file = text_preprocessing.build_class_file_list(files_path=file_path, i=user_data.id, word_vec=word_vec)
    print(f'list_file: {list_file.shape}')


    print("Making the predictions...")
    """
    predictions = []
    probas = []
    for item in list_file:
        # print(f"item: {item.shape}")
        prediction = ai.predict(item)
        proba_prediction = ai.predict_proba(item)

        probas.append(proba_prediction)
        predictions.append(prediction)
    # print(f"predictions: {np.ravel(predictions,order='C')}")
    print(f"transformed predictions: {le.inverse_transform(np.ravel(predictions,order='C'))}")
    print(f"predictions probas: {probas.shape}")
    """
    predictions = ai.predict(list_file)
    probas = ai.predict_proba(list_file)
    max_probs = [prob[prob.argmax()] for prob in probas]

    """
    print("Organizing the results...")
    unique_category_num = ['Data Science - 6', 'HR - 12', 'Advocate - 0', 'Arts - 1', 'Web Designing - 24',
                            'Mechanical Engineer - 16', 'Sales - 22', 'Health and fitness - 14',
                            'Civil Engineer - 5', 'Java Developer - 15', 'Business Analyst - 4',
                            'SAP Developer - 21', 'Automation Testing - 2', 'Electrical Engineering - 11',
                            'Operations Manager - 18', 'Python Developer - 20', 'DevOps Engineer - 8',
                            'Network Security Engineer - 17', 'PMO - 19', 'Database - 7', 'Hadoop - 13',
                            'ETL Developer - 10', 'DotNet Developer - 9', 'Blockchain - 3', 'Testing - 23']
    predictions_result = []
    for index in range(len(predictions)):
        for category in unique_category_num:
            category = category.split('-')

            if int(category[1]) == int(predictions[index]):
                files_dir = os.listdir('temp/extracted_{}'.format(user_data.id))

                folder_name = 'temp/extracted_{}'.format(user_data.id)

                for fname in files_dir:
                    path = os.path.join('temp/extracted_{}'.format(user_data.id), fname)
                    if os.path.isdir(path):
                        folder_name = "temp/extracted_{}/{}".format(user_data.id, fname)
                        break

                files_name = os.listdir(folder_name)

                prediction_json = {
                    "cargo": str(category[0]).strip(),
                    "curriculo": files_name[index],
                    "candidato": []
                }
                prediction_json = json.dumps(prediction_json)

                # predictions_result.append(("Item - " + str(index), "Category - " + str(category[0])))
                predictions_result.append(prediction_json)
    """

    predictions_result = []
    transformed_preds = le.inverse_transform(predictions)
    for index in range(len(transformed_preds)):
        folder_name = 'temp/extracted_{}'.format(user_data.id)
        files_dir = os.listdir(folder_name)

        for fname in files_dir:
            path = os.path.join(folder_name, fname)
            if os.path.isdir(path):
                folder_name = "temp/extracted_{}/{}".format(user_data.id, fname)
                break

        files_name = os.listdir(folder_name)
         
        prediction_json = {
            "certeza": "%.2f" % max_probs[index] + " %",
            "cargo": transformed_preds[index].strip(),
            "curriculo": files_name[index],
            "candidato": []
        }
        prediction_json = json.dumps(prediction_json)

        # predictions_result.append(("Item - " + str(index), "Category - " + str(category[0])))
        predictions_result.append(prediction_json)

    import pprint
    pprint.pprint(predictions_result)
    # print(f'\n predictions_result: {predictions_result} \n')

    pickled_result = pickle.dumps(predictions_result)
    user_data.raw_results = pickled_result
    user_data.save()
    process_results(request, file_path)
    # clear_temp_dir()
    

def process_results(request, file_path):
    # print(f"FILE PATH process_results: {file_path}")
    user_id = request.session['user_key']
    certainty = request.POST['certainty']
    certainty = str(float(certainty) * 0.01)

    try:
        user_data = Data.objects.get(user_key=user_id)
    except Data.DoesNotExist as data_unexist:
        user_data = None
        raise ValueError('Erro: {}'.format(data_unexist))

    user_json = pickle.loads(user_data.raw_results)
    keyword = user_data.key_word

    """
    # Salva o arquivo zip do usuario na pasta temp
    dir_name = Path(os.path.join("temp", "{}_user_zip".format(user_data.id)))
    dir_name.mkdir(parents=True, exist_ok=True)

    file_path = os.path.join("temp", f"{user_data.id}_user_zip", f"resumes{user_data.id}.zip")

    zipped_file = open(file_path, "wb+")
    zipped_file.write(user_data.file)
    zipped_file.close()
    """

    # Pega o caminho dos arquivos extraidos do zip pela funcao "build_class_file_list"
    extracted_folder = text_preprocessing.build_class_file_list(file_path, user_data.id, vectorize=False)

    # Pega o caminho contendo um zip com todos os pdfs filtrados
    filtered_pdfs_path, filtered_resumes = text_preprocessing.resume_filter_UPDATED(user_json, keyword, user_data.id, extracted_folder, certainty)

    # print(f"Filtered Pdfs Path: {filtered_pdfs_path.split('/')}")
    with open(filtered_pdfs_path, 'rb') as file:
        binary = file.read()

    # print(f'filtered_resumes: {filtered_resumes}')
    user_data.results = pickle.dumps(filtered_resumes)
    user_data.zipped_results = binary
    user_data.save()


def result(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    template_name = 'analyzer/result.html'
    template = loader.get_template(template_name)

    user_id = request.session['user_key']
    try:
        user_data = Data.objects.get(user_key=user_id)
    except Data.DoesNotExist as data_unexist:
        user_data = None
        raise ValueError('Erro: {}'.format(data_unexist))
    """
    dir_name = Path(os.path.join("uploads", "zips", "{}_user_zip".format(user_data.id)))
    dir_name.mkdir(parents=True, exist_ok=True)

    file_path = os.path.join("uploads", "zips", "{}_user_zip".format(user_data.id), "resumes{}.zip".format(user_data.id))

    zipped_file = open(file_path, "wb+")
    zipped_file.write(user_data.zipped_results)
    zipped_file.close()
    """
    # print(f"FILE PATH process_results: {file_path}")

    
    # Creating path to store the data to predict
    dir_name = Path(os.path.join("temp", f"{user_data.id}_results"))
    dir_name.mkdir(parents=True, exist_ok=True)

    # Getting the path containing data to predict
    file_path = os.path.join("temp", f"{user_data.id}_results", f"resumes_{user_data.id}.zip")

    # Writing the binary zipped user file to a zipfile
    zipped_file = open(file_path, "wb+")
    zipped_file.write(user_data.zipped_results)
    zipped_file.close()

    print(f"FILE PATH results: {file_path}")
    context = {
        'page_title': 'Result',
        'file_path' : file_path,
        'keyword': user_data.key_word
    }
    return HttpResponse(template.render(context, request))


def get_result(request):
    user_id = request.session['user_key']
    try:
        user_data = Data.objects.get(user_key=user_id)
    except Data.DoesNotExist as data_unexist:
        user_data = None
        raise ValueError('Erro: {}'.format(data_unexist))

    dir_name = Path(os.path.join("temp", "{}_user_zip".format(user_data.id)))
    dir_name.mkdir(parents=True, exist_ok=True)

    file_path = os.path.join("temp", "{}_user_zip".format(user_data.id), "resumes{}.zip".format(user_data.id))

    zipped_file = open(file_path, "wb+")
    zipped_file.write(user_data.file)
    zipped_file.close()

    user_json = pickle.loads(user_data.results)
    return HttpResponse(json.dumps(user_json['candidatos']), content_type='application/json')
    # print('USER_DATA.RESULT {}'.format(user_data.results))
    # print('USER_JSON: {}'.format(user_json))

    teste_json_item_1 = json.loads(user_json[0])

    return HttpResponse(json.dumps(teste_json_item_1['candidato']), content_type='application/json')


# Cria json a partir do model
def dynamicTableFromModel(data):
    data_json = []
    for i in data:
        obj = {}
        for k, v in i.items():
            obj[k] = v
            data_json.append(obj)
    return data_json

