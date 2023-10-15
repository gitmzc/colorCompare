from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response

import base64
import io
import json
from cmath import sqrt
from flask import Flask, request, jsonify
from dao import save_to_db,get_all_images,get_dominant_color
from flask_cors import cross_origin
import PIL.Image as Image


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

#
# @app.route('/api/count', methods=['POST'])
# def count():
#     """
#     :return:计数结果/清除结果
#     """
#
#     # 获取请求体参数
#     params = request.get_json()
#
#     # 检查action参数
#     if 'action' not in params:
#         return make_err_response('缺少action参数')
#
#     # 按照不同的action的值，进行不同的操作
#     action = params['action']
#
#     # 执行自增操作
#     if action == 'inc':
#         counter = query_counterbyid(1)
#         if counter is None:
#             counter = Counters()
#             counter.id = 1
#             counter.count = 1
#             counter.created_at = datetime.now()
#             counter.updated_at = datetime.now()
#             insert_counter(counter)
#         else:
#             counter.id = 1
#             counter.count += 1
#             counter.updated_at = datetime.now()
#             update_counterbyid(counter)
#         return make_succ_response(counter.count)
#
#     # 执行清0操作
#     elif action == 'clear':
#         delete_counterbyid(1)
#         return make_succ_empty_response()
#
#     # action参数错误
#     else:
#         return make_err_response('action参数错误')
#
#
# @app.route('/api/count', methods=['GET'])
# def get_count():
#     """
#     :return: 计数的值
#     """
#     counter = Counters.query.filter(Counters.id == 1).first()
#     return make_succ_response(0) if counter is None else make_succ_response(counter.count)



@app.route('/upload', methods=['POST'])
@cross_origin(supports_credentials=True)
def upload():

  file = request.files['file']
  img = file.read()
  image = Image.open(io.BytesIO(img))
  image = image.convert('RGB')

  feat = get_dominant_color(image)[0]
  print(get_dominant_color(image)[1])
  print(feat)

  save_to_db(img, feat)

  return 'Uploaded'


# @app.route('/search', methods=['POST'])
# @cross_origin(supports_credentials=True)
# def search():
#   file = request.files['file']
#
#   # 从 FileStorage 对象读取图片数据
#   img = file.read()
#   image = Image.open(io.BytesIO(img))
#   image = image.convert('RGB')
#
#   feat = get_dominant_color(image)[0]
#   print(get_dominant_color(image)[1])
#
#   result = query_db(feat)
#   print(result[0])
#   img_b64 = base64.b64encode(result[0]).decode('utf-8')
#   return jsonify({'img': img_b64})

@app.route('/search', methods=['POST'])
@cross_origin(supports_credentials=True)
def search():

  file = request.files['file']

  img = file.read()
  image = Image.open(io.BytesIO(img))
  image = image.convert('RGB')

  target_feat = get_dominant_color(image)[0]

  images = get_all_images()

  most_similar = find_most_similar(images, target_feat)
  print(most_similar[1])
  img_b64 = base64.b64encode(most_similar[1]).decode('utf-8')

  return jsonify({'img': img_b64})


def find_most_similar(images, target_feat):

  max_sim = 0
  result = None

  for id, img, feat_json in images:

    feat = json.loads(feat_json)

    sim = cosine_similarity(feat, target_feat)
    print(sim)

    if sim > max_sim:
      max_sim = sim
      result = [id, img]

  return result


def cosine_similarity(v1, v2):

  dot = sum(a*b for a,b in zip(v1,v2))
  mag1 = sqrt(sum(a**2 for a in v1))
  mag2 = sqrt(sum(b**2 for b in v2))

  sim = dot / (mag1 * mag2)
  return sim.real

