import datetime
from functools import wraps
import json

import requests
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging,jsonify
#from model.ConnecsiModel import ConnecsiModel
from passlib.hash import sha256_crypt
#from flask_oauthlib.client import OAuth
import os

connecsiApp = Flask(__name__)
connecsiApp.secret_key = 'connecsiSecretKey'
base_url = 'https://kiranpadwaltestconnecsi.pythonanywhere.com/api/'
# oauth = OAuth(connecsiApp)

# linkedin = oauth.remote_app(
#     'linkedin',
#     consumer_key='86ctp4ayian53w',
#     consumer_secret='3fdovLJRbWrQuu3u',
#     request_token_params={
#         'scope': 'r_basicprofile,r_emailaddress',
#         'state': 'RandomString',
#     },
#     base_url='https://api.linkedin.com/v1/',
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
#     authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
# )

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('index'))
    return wrap


@connecsiApp.route('/')
# @is_logged_in
def index():
    title='Connesi App Login Panel'
    data=[]
    data.append(title)
    return render_template('user/login.html',data=data)


# @connecsiApp.route('/loginLinkedin')
# def loginLinkedin():
#     return linkedin.authorize(callback=url_for('authorized', _external=True))

@connecsiApp.route('/registerBrand')
def registerBrand():
    return render_template('user/registerFormBrand.html')

@connecsiApp.route('/saveBrand',methods=['GET','POST'])
def saveBrand():
    if request.method == 'POST':
        url = base_url+'Brand/register'
        payload = request.form.to_dict()
        print(payload)
        del payload['confirm_password']
        print(payload)
        title = 'Connesi App Login Panel'
        try:
            response = requests.post(url, json=payload)
            print(response.json())
            result_json = response.json()
            print(result_json['response'])
            result = result_json['response']
            # exit()
            if result == 1:
                flash("Brand Details Successfully Registered", 'success')
                title = 'Connesi App Login Panel'
                return render_template('user/login.html', title=title)
            else:
                flash("Internal error please try later", 'danger')
                return render_template('user/login.html', title=title)
        except:
            flash("Internal error please try later", 'danger')
            return render_template('user/registerFormBrand.html',title='Register Brand')
#
#
#
#Logout
@connecsiApp.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('index'))

#
# # User login
@connecsiApp.route('/login',methods=['POST'])
def login():
    if request.method=='POST':
        if 'brand' in request.form:
            url = base_url + 'User/login'
            payload = request.form.to_dict()
            print(payload)
            del payload['brand']
            print(payload)
            title = ''
            try:
                response = requests.post(url, json=payload)
                print(response.json())
                result_json = response.json()
                user_id = result_json['user_id']
                print(user_id)
                # exit()
                if user_id:
                    flash("logged in", 'success')
                    session['logged_in'] = True
                    session['email_id']=payload.get('email')
                    session['type'] = 'brand'
                    session['user_id']=user_id
                    print(session['user_id'])
                    return redirect(url_for('admin'))
                else:
                    flash("Internal error please try later", 'danger')
                    return render_template('user/login.html', title=title)
            except:
                flash("Internal error please try later", 'danger')
                return render_template('user/login.html', title='Login')
        elif 'influencer' in request.form:
            email_id = request.form.get('inf_username')
            password = request.form.get('inf_password')
            print(email_id)
            print(password)

@connecsiApp.route('/admin')
@is_logged_in
def admin():
    title='Dashboard'
    return render_template('index.html',title=title)
#
#
@connecsiApp.route('/profileView')
@is_logged_in
def profileView():
    title='Profile View'
    type = session['type']
    user_id = session['user_id']
    if type == 'brand':
        url = base_url + 'Brand/'+str(user_id)
        try:
            response = requests.get(url)
            # print(response.json())
            data_json = response.json()
            print(data_json)
            return render_template('user/user-profile-page.html', data=data_json, title=title)
        except Exception as e:
            print(e)
    else:
        table_name = 'users_inf'



@connecsiApp.route('/editProfile')
@is_logged_in
def editProfile():
    title='Edit Profile'
    type = session['type']
    user_id = session['user_id']
    if type == 'brand':
        url = base_url + 'Brand/'+str(user_id)
        try:
            response = requests.get(url)
            # print(response.json())
            data_json = response.json()
            print(data_json)
            return render_template('user/edit-profile-page.html', data=data_json, title=title)
        except Exception as e:
            print(e)
    else:
        table_name = 'users_inf'

@connecsiApp.route('/updateProfile',methods=['GET','POST'])
@is_logged_in
def updateProfile():
    user_id = session['user_id']
    if request.method == 'POST':
        url = base_url+ 'Brand/'+str(user_id)
        payload = request.form.to_dict()
        print(payload)
        try:
            response = requests.put(url=url,json=payload)
            result_json = response.json()
            # return redirect(url_for('/profileView'))
            return profileView()
        except:pass


@connecsiApp.route('/searchInfluencers',methods=['POST','GET'])
@is_logged_in
def searchInfluencers():
    url_regionCodes = base_url + 'Youtube/regionCodes'
    regionCodes_json=''
    videoCat_json=''
    form_filters=''
    country_name=''
    try:
        response_regionCodes = requests.get(url=url_regionCodes)
        regionCodes_json = response_regionCodes.json()
        # print(regionCodes_json['data'])
    except Exception as e:
        print(e)
    url_videoCat = base_url + 'Youtube/videoCategories'
    try:
        response_videoCat = requests.get(url=url_videoCat)
        videoCat_json = response_videoCat.json()
        # print(videoCat_json['data'])
    except Exception as e:
        print(e)
    lookup_string = ''
    for cat in videoCat_json['data']:
        # print(cat['video_cat_name'])
        lookup_string += ''.join(',' + cat['video_cat_name'])
    lookup_string = lookup_string.replace('&', 'and')

    if request.method=='POST':
        if 'search_inf' in request.form:
            string_word = request.form.get('string_word')
            print(string_word)
            # exit()
            category = string_word.replace('and','&')
            print(category)
            category_id=''
            for cat in videoCat_json['data']:
                # print(cat['video_cat_name'])
                if cat['video_cat_name'] == category:
                    print("category id = ",cat['video_cat_id'])
                    category_id = cat['video_cat_id']
            form_filters = request.form.to_dict()
            print(form_filters)
            url_country_name = base_url + 'Youtube/regionCode/'+form_filters['country']
            try:
                response_country_name = requests.get(url=url_country_name)
                country_name_json = response_country_name.json()
                print(country_name_json['data'][0][1])
                country_name = country_name_json['data'][0][1]
            except Exception as e:
                print(e)
            form_filters.update({'country_name':country_name})
            payload = request.form.to_dict()

            del payload['string_word']
            del payload['search_inf']
            del payload['channel']
            payload.update({'category_id': str(category_id)})
            payload.update({'min_lower':payload.get('min_lower')})
            payload.update({'max_upper':payload.get('max_upper')})
            print(payload)
            try:
                channel = request.form.get('channel')
                url = base_url+'Youtube/searchChannels/'+channel
                # print(url)
                response = requests.post(url, json=payload)
                print(response.json())
                data = response.json()
                return render_template('search/searchInfluencers.html', regionCodes=regionCodes_json,
                                       lookup_string=lookup_string, form_filters=form_filters,data=data)
            except Exception as e:
                print(e)
            return render_template('search/searchInfluencers.html', regionCodes=regionCodes_json,
                                   lookup_string=lookup_string,form_filters=form_filters)

    else:
        return render_template('search/searchInfluencers.html', regionCodes=regionCodes_json,
                               lookup_string=lookup_string,form_filters=form_filters,data='')



#
@connecsiApp.route('/addFundsBrands')
@is_logged_in
def addFundsBrands():
    return render_template('user/add_funds.html')


@connecsiApp.route('/saveFundsBrands',methods=['POST'])
@is_logged_in
def saveFundsBrands():
    if request.method == 'POST':
       payload = request.form.to_dict()
       print(payload)
       user_id = session['user_id']
       url = base_url+'Payments/'+str(user_id)
       try:
           response = requests.post(url=url, json=payload)
           result_json = response.json()
           return viewMyPayments()
       except:
           pass
    else:
        return redirect(url_for('addFundsBrands'))

#
# @connecsiApp.route('/payment')
# @is_logged_in
# def payment():
#     # print(user_id,date,email_id,amount,description)
#     return render_template('payment/payment.html')
#
# @connecsiApp.route('/checkout')
# @is_logged_in
# def checkout():
#     return redirect(url_for('viewMyPayments'))
#
@connecsiApp.route('/viewMyPayments')
@is_logged_in
def viewMyPayments():
    data = ''
    user_id = session['user_id']
    url = base_url + 'Payments/'+str(user_id)
    try:
        response = requests.get(url=url)
        data = response.json()
        print(data)
        return render_template('user/view_my_payments.html', data=data)
    except:
        pass
    return render_template('user/view_my_payments.html',data=data)
#
#
@connecsiApp.route('/add_Campaign')
@is_logged_in
def add_Campaign():
    #connecsiObj = ConnecsiModel()
    #region_codes = connecsiObj.get__(table_name='youtube_region_codes',STAR='*')
    #video_categories = connecsiObj.get__(table_name='youtube_video_categories', STAR='*')
    return render_template('campaign/add_campaignForm.html')


@connecsiApp.route('/viewCampaigns')
@is_logged_in
def viewCampaigns():
    #connecsiObj = ConnecsiModel()
    #region_codes = connecsiObj.get__(table_name='youtube_region_codes',STAR='*')
    #video_categories = connecsiObj.get__(table_name='youtube_video_categories', STAR='*')
    return render_template('campaign/viewCampaigns.html')

@connecsiApp.route('/viewCampaignDetails')
@is_logged_in
def viewCampaignDetails():
    #connecsiObj = ConnecsiModel()
    #region_codes = connecsiObj.get__(table_name='youtube_region_codes',STAR='*')
    #video_categories = connecsiObj.get__(table_name='youtube_video_categories', STAR='*')
    return render_template('campaign/viewCampaignDetails.html')


# @connecsiApp.route('/saveCampaign',methods=['POST'])
# @is_logged_in
# def saveCampaign():
#     if request.method == 'POST':
#         campaign_name = request.form.get('campaign_name')
#         from_date = request.form.get('from_date')
#         to_date = request.form.get('to_date')
#         budget = request.form.get('budget')
#         currency = request.form.get('currency')
#         channels = request.form.getlist('channel')
#         channels_string = ','.join(channels)
#         regions = request.form.getlist('region')
#         regions_string = ','.join(regions)
#         min_lower = request.form.get('min_lower')
#         max_upper = request.form.get('max_upper')
#
#         files = request.form.getlist('files')
#         # files = request.files.getlist("files")
#         print(files)
#
#         video_cat = request.form.get('video_cat')
#         target_url = request.form.get('target_url')
#         campaign_description = request.form.get('campaign_description')
#         arrangements = request.form.getlist('arrangements')
#         arrangements_string=','.join(arrangements)
#         kpis = request.form.get('kpis')
#         user_id = session['user_id']
#         data=[campaign_name,from_date,to_date,budget,currency,channels_string,
#               regions_string,min_lower,max_upper,video_cat,target_url,campaign_description,arrangements_string,kpis,user_id]
#         columns = ['campaign_name','from_date','to_date','budget','currency','channels','regions',
#                    'min_lower_followers','max_upper_followers','video_cat_id','target_url','campaign_description','arrangements','kpis','user_id']
#         connecsiObj = ConnecsiModel()
#         connecsiObj.insert__(table_name='brands_campaigns',columns=columns,data=data)
#         return ""
#
@connecsiApp.route('/inbox')
@is_logged_in
def email():
    return render_template('email/inbox.html')

# @connecsiApp.route('/login/authorized')
# def authorized():
#     resp = linkedin.authorized_response()
#     if resp is None:
#         return 'Access denied: reason=%s error=%s' % (
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     session['linkedin_token'] = (resp['access_token'], '')

    # me = linkedin.get('people/~')
    # email_linkedin = linkedin.get('people/~:(email-address)')
    # print(jsonify(email_linkedin.data))

    # email_id = email_linkedin.data['emailAddress']
    # data=[me.data['id'],me.data['firstName'],me.data['lastName'],email_id,'',me.data['headline'],'Admin']
    # print(me.data)
    # session['logged_in'] = True
    # session['type'] = 'brand'
    # session['user_id'] = me.data['id']
    # session['first_name']=me.data['firstName']
    # print(data)
    # return render_template('index.html',data=data)

# @linkedin.tokengetter
# def get_linkedin_oauth_token():
#     return session.get('linkedin_token')


# def change_linkedin_query(uri, headers, body):
#     auth = headers.pop('Authorization')
#     headers['x-li-format'] = 'json'
#     if auth:
#         auth = auth.replace('Bearer', '').strip()
#         if '?' in uri:
#             uri += '&oauth2_access_token=' + auth
#         else:
#             uri += '?oauth2_access_token=' + auth
#     return uri, headers, body
#
# linkedin.pre_request = change_linkedin_query

if __name__ == '__main__':
    connecsiApp.secret_key = 'connecsiSecretKey'
    connecsiApp.run(debug=True,host='localhost',port=8090)