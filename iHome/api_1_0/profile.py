#coding:utf-8
#个人中心

from flask import current_app,jsonify,request,g

from iHome import db,constants
from iHome.models import User
from iHome.utils.commom import login_required
from iHome.utils.image_storge import upload_image
from iHome.utils.response_code import RET
from . import api

@api.route('/users/auth',methods=["GET"])
@login_required
def get_user_auth():
    """提供实名认证数据
        0.判断用户是否登录
        1.查询当前登录用户user信息
        2.构造响应的实名认证的数据
        3.响应实名认证的数据
    """
    #1.查询当前登录用户user信息
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='用户不存在')

    #2.构造响应的实名认证的数据
    response_auth_dict = user.auth_to_dict()

    #3.响应实名认证的数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_auth_dict)


@api.route('/users/auth',methods=["POST"])
@login_required
def set_user_auth():
    """实名认证
        0.判断用户是否登录
        1.获取实名认证参数：real_name,id_card,并判断是否为空
        2.查询当前的登录用户user模型
        3.将real_name,id_card赋值给user模型
        4.保存到数据库
        5.响应实名认证结果
    """
    # 1.获取实名认证参数：real_name,id_card,并判断是否为空
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')
    if not all([real_name,id_card]):# 实际开发中，需要对身份证号码格式校验。一般会使用第三方的平台实名认证
        return jsonify(errno=RET.PARAMERR,errmsg='缺少参数')

    #2.查询当前的登录用户user模型
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='用户不存在')

    #3.将real_name,id_card赋值给user模型
    user.real_name = real_name
    user.id_card = id_card

    #4.保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存新的用户名失败')

    #5.响应实名认证结果
    return jsonify(errno=RET.OK,errmsg='实名认证成功')

@api.route('/users/name',methods=["PUT"])
@login_required
def set_user_name():
    """修改用户名
        0.TODO 判断用户是否登录
        1.获取新的用户名，并判断是否为空
        2.查询当前的登录用户
        3.将新的用户名赋值给当前的登录用户的user模型
        4.将数据保存到数据库
        5.响应修改用户名的结果
        """
    # 1.获取新的用户名，并判断是否为空
    new_name = request.json.get('name')
    if not new_name:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')

    # 2.查询当前的登录用户
    # user_id = session['user_id']
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='用户不存在')

    # 3.将新的用户名赋值给当前的登录用户的user模型
    user.name = new_name

    # 4.将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存新的用户名失败')

    # 5.响应修改用户名的结果
    return jsonify(errno=RET.OK, errmsg='修改用户名成功')


@api.route('/users/avatar',methods=["POST"])
@login_required
def upload_avatar():
    """上传用户头像
    0.TODO 判断用户是否登录
    1.获取用户上传的头像数据，并校验
    2.查询当前的登录用户
    3.调用上传工具方法实现用户头像的上传
    4.将用户头像赋值给当前的登录用户的user模型
    5.将数据保存到数据库
    6.响应上传用户头像的结果
    """
    # 1.获取用户上传的头像数据，并校验
    try:
        avatar_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='获取用户头像失败')
    # 2.查询当前的登录用户
    # user_id = session['user_id']
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='用户不存在')

    # 3.调用上传工具方法实现用户头像的上传
    try:
        key = upload_image(avatar_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传用户头像失败')
    # 4.将用户头像赋值给当前的登录用户的user模型
    user.avatar_url = key

    # 5.将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户头像失败')

    # 6.响应上传用户头像的结果
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传用户头像成功',data=avatar_url)


@api.route('/users',methods=["GET"])
@login_required
def get_user_info():
    """提供个人信息
    0.TODO 判断用户是否登录
    1.从session中获取当前登录用户的user_id
    2.查询当前登录用户的user信息
    3.构造个人信息的响应数据
    4.响应个人信息的结果
    """

    # 1.查询当前登录用户user信息
    # user_id = session['user_id']
    user_id = g.user_id

    # 2.查询当前登录用户的user信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 3.构造个人信息的响应数据：思考响应哪些数据给用户
    response_info_dict = user.to_dict()

    return jsonify(errno=RET.OK, errmsg='OK', data=response_info_dict)