from django.db import models
from django.shortcuts import render
from myapp.models import Article, Comment, UserInfo, CommentLikes,ArticleLikes,Tags
from django.http import HttpResponse
from datetime import datetime
import json,urllib2
import os
import shutil
from os import rename, listdir
from django.http import HttpResponseRedirect
from datetime import datetime
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.shortcuts import render
from passlib.hash import  md5_crypt
from django.shortcuts import get_object_or_404

# Create your views here.


def article (request, art_id):


		if 'logged' in request.session:
			logged = 1
		else:
			
			logged = 0

		article = get_object_or_404(Article, pk=art_id , published=1)
		#article likes:
		artLikes = ArticleLikes.objects.filter(articleId= art_id).count()  #all likes on comment

		
		article.image= (str(article.image))[6:]
		try:
			userinf = UserInfo.objects.get(name= request.session['username'])

			#if user likes the article
			userLikeArticle = ArticleLikes.objects.filter(userId= userinf.id ,articleId= art_id).exists()  #user likes the article

			#if commented from form
			if 'comment' in request.POST:  #save comment
				commContent =request.POST['comment']
				par_id =request.POST['parentID']
				if par_id =='':   #comment on artticle --> comment field = NULL
					par_id=None
				dateTime =  datetime.now()
				newComment= Comment(content= commContent , date=dateTime ,  userId  = userinf ,  articleId= article , commentId= par_id)
				newComment.save()
		except:
			userinf=None
			userLikeArticle=None


		

		#separating comments
		reply_comments= []
		parent_comments=[]
		likedByUser= []
	
		try:
			comments = Comment.objects.filter(articleId=art_id  ).select_related('userId').order_by('id')   #all comments
			comments.select_related = False  #to enable edit in comment fields

			for comm in comments :

					#slice image path (remove "myapp")
					comm.userId.profilepicture = (str(comm.userId.profilepicture))[6:]

					try:	
						#add like attribute (containing num of likes) to cmment object
						likes = CommentLikes.objects.filter(commentId= comm.id)  #all likes on comment
						comm.likes = likes.count

						#if user liked the comment
						if userinf:
							liked =  likes.values_list('commentId', flat=True).filter(userId= userinf.id)  
							if liked:
								likedByUser.extend (liked) 

					except:
						comm.likes = 0

					if comm.commentId:  #not none
						reply_comments.append(comm)   	#reply comments

					else :
						parent_comments.append(comm) 	#parent comments


				
		except:  #no comments found
			comments = None

		
		
                listOfArticle=[] 
                words=[] 
                keyWords =Tags.objects.filter(relatedId=art_id)
                #for on every word to get related articles id

                for tempWord in keyWords:
                       nomyword=Tags.objects.filter(word=tempWord.word)            
                       if len(nomyword)>1 :
                           words.append(nomyword[0].word)
                           articles=Tags.objects.filter(word=nomyword[0].word).exclude(relatedId=art_id)
                           for myarticle in articles:
                               if myarticle.relatedId.id not in  listOfArticle :
                                      listOfArticle.append(myarticle.relatedId.id)    
                


		if userinf:
			username = request.session['username']
		else:
			username=None



		return render(request,'article.html',{ 'username':  username  ,'article': article  , 'parent' : parent_comments, 'replies' :reply_comments , 'liked' :likedByUser , 'artLikes':artLikes , 'userArt': userLikeArticle,'listOfArticle':listOfArticle  , 'logged':logged}  )
def like(request, art_id , cmt_id):


	userinf = UserInfo.objects.get(name= request.session['username'])
	if (int (cmt_id) == 0): 	#like the article
		article = Article.objects.get(pk=art_id)		
		like= ArticleLikes(userId= userinf , articleId=article )
	else:			#like the comment/reply	
		comment = Comment.objects.get(pk=cmt_id)
		like= CommentLikes(userId= userinf , commentId=comment )
	
	like.save()
	return redirect('/article/'+art_id+'/')


def unlike(request, art_id , cmt_id):

	userinf = UserInfo.objects.get(name= request.session['username'])
	
	if (int (cmt_id) == 0): 	#like the article
		article = Article.objects.get(pk=art_id)				
		ArticleLikes.objects.get(userId= userinf , articleId=article).delete()
	else:
		comment = Comment.objects.get(pk=cmt_id)
		CommentLikes.objects.get(userId= userinf , commentId=comment ).delete()

	return redirect('/article/'+art_id+'/')





def all_articles(request):
	article_data = Article.objects.all().filter(published=1).order_by('-date')
	article_count=Article.objects.all().filter(published=1).count()

	if 'logged' in request.session:
		return render(request,'all_articles.html',{'username':request.session['username'],'logged' : 1 , 'myarticle' : article_data , 'mycount' : article_count})

	else:
		return render(request,'all_articles.html',{'logged' : 0 , 'myarticle' : article_data , 'mycount' : article_count})



def home(request):
	articles = Article.objects.all().filter(published=1).order_by('-date')[:5]

	if 'logged' in request.session:
		return render(request,'home.html',{'username':request.session['username'],'logged': 1,'article': articles})
	else:
		return render(request,'home.html',{'logged': 0,'article': articles})





def facebooklogin(request):
	try:
		
                social_user = request.user.social_auth.filter(provider='facebook',).first() 	
	        
		url = u'https://graph.facebook.com/{0}?' \
				 u'&access_token={1}'.format(
				      social_user.uid,
				      social_user.extra_data['access_token'],
				  )      
		myrequest = urllib2.Request(url)
		UserInfoObject = json.loads(urllib2.urlopen(myrequest).read())
                FbId=UserInfoObject['id'] 
		nameg=UserInfoObject['first_name']
		emailg=UserInfoObject['email'] 
		request.user.social_auth.filter(provider='facebook',).first().delete()
		url2 = 'https://graph.facebook.com/{0}/picture?width=100&height=100&redirect=false&access_token={1}'.format(
					      social_user.uid,
					      social_user.extra_data['access_token'],
					  )      
		myrequest2 = urllib2.Request(url2)
		picture = json.loads(urllib2.urlopen(myrequest2).read())
		pictureUrl=picture['data']['url']
                if UserInfoObject['name']==None or UserInfoObject['email']==None:
				return render(request,'home.html')

		else:
		                
		                if (len(UserInfo.objects.filter(email=emailg))==1):
					users_matches = UserInfo.objects.get(email=emailg)				
					users_matches.facebookId=FbId
					users_matches.hasfacebook=True
					users_matches.save()
                                        request.session['logged']=True
					request.session['username']=users_matches.name
					request.session['userid']=users_matches.id
					return HttpResponseRedirect("/home/",{'username':users_matches.name,'logged':1})		 
				#else:
				
				#	request.session['logged']=True
				#	request.session['username']=nameg
				#	request.session['facebook_unknown']=True
				#	return render(request,'home.html')
			        else:
		                        request.session['logged']=True
					request.session['username']=UserInfoObject['first_name']
					return render(request,'facebookregister.html',{'FbId':FbId,'nameg':nameg,'emailg':emailg,'profilepicture':pictureUrl,'username':request.session['username'],'logged':1})
	       	  
	except:
		return HttpResponseRedirect('/home/',{'logged':1})        
    

        
def facebookregister(request):
  try:   
        social_user = request.user.social_auth.filter(provider='facebook',).first() 	
        #return HttpResponse(auth_user.email)
        url = u'https://graph.facebook.com/{0}?' \
			 u'&access_token={1}'.format(
			      social_user.uid,
			      social_user.extra_data['access_token'],
			  )   
	myrequest = urllib2.Request(url)
	UserInfoObject = json.loads(urllib2.urlopen(myrequest).read())
	FbId=UserInfoObject['id'] 
	nameg=UserInfoObject['first_name']
	emailg=UserInfoObject['email'] 
        url2 = 'https://graph.facebook.com/{0}/picture?width=100&height=100&redirect=false&access_token={1}'.format(
					      social_user.uid,
					      social_user.extra_data['access_token'],
					  )      
	myrequest2 = urllib2.Request(url2)
	picture = json.loads(urllib2.urlopen(myrequest2).read())
	pictureUrl=picture['data']['url']
	request.user.social_auth.filter(provider='facebook',).first().delete()
	if UserInfoObject['name']==None or UserInfoObject['email']==None:
			return render(request,'index.html',{'logged':0})

	else:
                        if (len(UserInfo.objects.filter(email=emailg))==1):
				users_matches = UserInfo.objects.get(email=emailg)
 		                users_matches.facebookId=FbId
				users_matches.hasfacebook=True
                                users_matches.save()   
                                request.session['logged']=True
				request.session['username']=UserInfoObject['first_name']
                                request.session['userid']=users_matches.id
                                return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})		
				
			else:
				request.session['logged']=True
				request.session['username']=nameg
				return render(request,'facebookregister.html',{'FbId':FbId,'nameg':nameg,'emailg':emailg,'profilepicture':pictureUrl,'username':request.session['username'],'logged':1})
					
				
  except:
    		return HttpResponseRedirect('/home/',{'logged':0})
 
def index(request):
	#check cookie
					#request.session['logged']=True
					#request.session['username']=username
        return HttpResponseRedirect("/home/",{'logged':0})#kan home 			
	#return HttpResponseRedirect("/index/",{'logged':0})#kan home
	

		 
def register(request):
	if 'logged' in request.session:
		return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1}) 
	else:
		return render(request,'register.html',{'logged':0})	


def saveUserfacebook(request):		
 
	try:
#check if username or password or email or repassword = none go to register.html again
             #if form.is_valid():  
		if request.POST['username'] ==None or request.POST['password']  ==None or  request.POST['email']  ==None or  request.POST['repassword']  ==None:
			return render(request,'register.html',{'logged':0})

#check if password not equels repassword go to register.html again
		elif request.POST['password'] != request.POST['repassword']:
			return render(request,'register.html',{'logged':0})
		if request.POST.get('facebookid') ==False:
                       user = UserInfo(name=request.POST['username'],password=rmd5_crypt.encrypt(request.POST['password']),email=request.POST['email'])
		
                else :
                       user = UserInfo(name=request.POST['username'],password=md5_crypt.encrypt(request.POST['password']),email=request.POST['email'],facebookId=request.POST.get('facebookid'),hasfacebook=True)
		pictureUrl=request.POST.get('myimage', False)
                
                if 'image' in request.FILES: 
			user.profilepicture=request.FILES['image']
                    
                elif pictureUrl!=False:
                        
				img_temp = NamedTemporaryFile()
				img_temp.write(urllib2.urlopen(pictureUrl).read())
				img_temp.flush()
		                user.profilepicture=File(img_temp)
                            
		user.save()
		request.session['logged']=True
		request.session['username']=request.POST['username']
                
		try:
                 	
			if 'image' in request.FILES : 
		                        
					#get user id and his image path
					user = UserInfo.objects.get(name=request.POST['username'],password=request.POST['password'])
					current_user_id =user.id
					current_user_profilepicture =user.profilepicture
					#myapp/static/users/xxx.jpg
					extenstion= '.'+str(current_user_profilepicture).split('/')[3].split('.')[1]
					os.rename(str(current_user_profilepicture),'myapp/static/users/'+str(current_user_id)+extenstion)
					user.profilepicture ='myapp/static/users/'+str(current_user_id)+extenstion
					user.save()
		                        return HttpResponseRedirect("/home/",{'logged':1})
		        if  pictureUrl!=False:    
				        user = UserInfo.objects.get(name=request.POST['username'],password=request.POST['password'])
					current_user_id =user.id
					current_user_profilepicture =user.profilepicture
					#myapp/static/users/xxx.jpg
					extenstion= '.'+"jpg"
					os.rename(str(current_user_profilepicture),'myapp/static/users/'+str(current_user_id)+extenstion)
					user.profilepicture ='myapp/static/users/'+str(current_user_id)+extenstion
					user.save()
		                        return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})


		except:  
			return HttpResponseRedirect("/home/",{'logged':0})

		return HttpResponseRedirect("/home/",{'logged':0})		
		
		 
	except:
		return HttpResponseRedirect("/home/",{'logged':0})
	
def saveUser(request):		

	try:
#check if username or password or email or repassword = none go to register.html again

		if request.POST['username'] ==None or request.POST['password']  ==None or  request.POST['email']  ==None or  request.POST['repassword']  ==None:
			return render(request,'register.html')

#check if password not equels repassword go to register.html again
		elif request.POST['password'] != request.POST['repassword']:
			return render(request,'register.html',{'logged':0})

		users_matches = UserInfo.objects.all().filter(name=request.POST.get('username'))


		if len(users_matches) >= 1:
			return render(request,'register.html', {'registerMessage' : 'username already taken','username' : request.POST.get('username'),'email' : request.POST.get('email'),'logged':0 })



		users_matches = UserInfo.objects.all().filter(email=request.POST.get('email'))

		if len(users_matches) >= 1:
			return render(request,'register.html', {'registerMessage' : 'email already taken','username' : request.POST.get('username'),'email' : request.POST.get('email'), 'logged':0})

		user = UserInfo(name=request.POST['username'],password=md5_crypt.encrypt(request.POST['password']),email=request.POST['email'])
		if 'image' in request.FILES: 
			user.profilepicture=request.FILES['image']

		user.save()
		request.session['logged']=True
		request.session['username']=request.POST['username']
		try:	
			if 'image' in request.FILES: 

				#get user id and his image path
				user = UserInfo.objects.get(name=request.POST['username'],password=request.POST['password'])
				current_user_id =user.id
				current_user_profilepicture =user.profilepicture
				#myapp/static/users/xxx.jpg
				extenstion= '.'+str(current_user_profilepicture).split('/')[3].split('.')[1]
				os.rename(str(current_user_profilepicture),'myapp/static/users/'+str(current_user_id)+extenstion)
				user.profilepicture ='myapp/static/users/'+str(current_user_id)+extenstion
				user.save()
				return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})
		
		except:  
				return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})

		return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})		
		
		 
	except:
		return render(request,'register.html',{'logged':0})

def login(request):
		if 'logged' in request.session:
			logged = 1
		else:
			
			logged = 0

		
		try:
                
			a= (request.POST.get('mynewindex'))
			#chick come for next time		
			if a == "1":
		                           
				if request.POST.get('forgetme')!=None:
					response = HttpResponseRedirect("/index/",{'logged':0})
					response.set_cookie("remember_username", "",-1)					        
					request.session['logged']=False
					request.session['username']=request.POST.get('username')
					return response
				


			#come for next time		
			else:
		            
				if request.COOKIES.has_key( 'remember_username' ):
					username = request.COOKIES[ 'remember_username' ]
					#password = request.COOKIES[ 'remember_password' ]
					users_matches = UserInfo.objects.all().filter(name=username)
					if len(users_matches) >= 1 :
								return render(request,'index.html',{'logged':0,'username':username,'newindex':1})


			if request.POST.get('username')==None or request.POST.get('password')==None:
				return render(request,'index.html',{'logged':0})
			else:
				users_matches = UserInfo.objects.all().filter(name=request.POST.get('username'))

				if len(users_matches) < 1:
					return render(request,'index.html', {'loginMessage' : 'invalid username','logged':0})#kant 1

				else:

					if md5_crypt.verify(request.POST.get('password'),users_matches[0].password):
		                                    #return   HttpResponse("hi")					
						if request.POST.get('remember')!=None:
							response = HttpResponseRedirect("/home/",{'logged':1})						
							response.set_cookie('remember_username', request.POST.get('username') , max_age=60*10)
							request.session['logged']=True
							request.session['username']=request.POST.get('username')

							return response


						elif request.POST.get('forgetme')!=None:
							response = HttpResponseRedirect("/index/",{'logged':0})
							 
							#return   HttpResponse("hi2")	
							
							response.set_cookie("remember_username", "",-1)					        

							request.session['logged']=False
							request.session['username']=request.POST.get('username')

							return response
		                                    
						else:
							request.session['logged']=True
							request.session['username']=request.POST.get('username')
							return HttpResponseRedirect("/home/",{'username':request.session['username'],'logged':1})		

					else:
						return render(request,'index.html', {'loginMessage' : 'invalid username or password','logged':0})
		except:				
				return HttpResponseRedirect("/home/",{'logged':0})		



def logout(request):
	if 'logged' in request.session:
		del request.session['logged']
		del request.session['username'] 
	return HttpResponseRedirect("/home/",{'logged':0})





def notvalid(request):
	return render(request,'notvalid.html')


def profile (request):
	try:
		if 'username' in request.session:
			users_match = UserInfo.objects.all().filter(name=request.session['username'])[0]
			
			if users_match != None and users_match.password != None:	
				username =users_match.name
				email = users_match.email
				userimage = str(users_match.profilepicture)[6:]
				return render(request,'profile.html', {'username' : username, 'email': email , 'userimage':userimage })
			else:
				return HttpResponseRedirect("/home/")
		else:
			return HttpResponseRedirect("/home/")
	except:
		return HttpResponseRedirect("/home/")



def updateprofile(request):		
	
	try:
		
		if request.POST['username'] ==None  or  request.POST['email']  ==None:
			return render(request,'profile.html')

		users_old_data = UserInfo.objects.all().filter(name=request.session['username'])[0]
		
		
		if users_old_data.name != request.POST.get('username'):
			users_matches = UserInfo.objects.all().filter(name=request.POST.get('username'))
			
			if len(users_matches) >= 1:
				image=str(users_old_data.profilepicture)[6:]
				return render(request,'profile.html', {'userimage':image,'registerMessage' : 'username already taken','username' : request.POST.get('username'),'email' : request.POST.get('email') })
			else:
				
				user = UserInfo.objects.get(id=users_old_data.id)
				user.name=request.POST.get('username')
				user.save()						
				request.session['username'] = request.POST.get('username')




		if users_old_data.email != request.POST.get('email'):
			users_matches = UserInfo.objects.all().filter(email=request.POST.get('email'))
			
			if len(users_matches) >= 1:
				image=str(users_old_data.profilepicture)[6:]
				return render(request,'profile.html', {'userimage':image,"registerMessage" : 'email already taken','username' : request.POST.get('username'),'email' : request.POST.get('email') ,'username':request.session['username'],'logged':1})
			else:
				
				user = UserInfo.objects.get(id=users_old_data.id)
				user.email=request.POST.get('email')
				user.save()						


		if 'image' in request.FILES:
			
			user = UserInfo.objects.get(id=users_old_data.id)
			user.profilepicture=request.FILES['image']
			user.save()
			#return HttpResponse(user.profilepicture)

		try:	
			if 'image' in request.FILES: 

				#get user id and his image path
				user = UserInfo.objects.get(id=users_old_data.id)
				current_user_id =user.id
				current_user_profilepicture =user.profilepicture
				#myapp/static/users/xxx.jpg
				extenstion= '.'+str(current_user_profilepicture).split('/')[3].split('.')[1]
				os.rename(str(current_user_profilepicture),'myapp/static/users/'+str(current_user_id)+extenstion)
				user.profilepicture ='myapp/static/users/'+str(current_user_id)+extenstion
				user.save()
				
		
		except:  
			return HttpResponseRedirect("/profile/",{'username':request.session['username'],'logged':1})
		return HttpResponseRedirect("/profile/",{'username':request.session['username'],'logged':1})
	except:
		return HttpResponseRedirect("/profile/",{'username':request.session['username'],'logged':1})	



def forgetpass(request):
		return  render(request,'repass.html')


def sendmail(request):
				try:
					user = UserInfo.objects.get(email=request.POST.get('email'))
				except:
					return render(request,'index.html', {'loginMessage' : 'invalid email'})
					
				try:
					message = "Please, follow the folloing link to renew your email: \n   http://127.0.0.1:8000/renew/?n="+str (user.id)
					email = str (user.email)
					email = EmailMessage('Change password request', message, to=[email])
					email.send()
					return render(request,'index.html', {'loginMessage' : 'Please,check your email and come back to log in after renewing password.'})
				except:
					return render(request,'index.html', {'loginMessage' : 'Can not send email, an error occurred.'})


def renew (request):

		if 'n' in request.GET:  #save comment
			return render(request,'renewPassword.html',{"id":request.GET['n']})  
		else:

			 return render(request,'home.html', {'username':request.session['username'],'logged' : 1 })  #not logged?


def savepass (request):
		password=md5_crypt.encrypt(request.POST['password'])
		iD =request.POST['id']

		user = UserInfo.objects.get(pk=iD) # object to update
		user.password =password # update name
		user.save() # save object
		return render(request,'home.html', {'username':request.session['username'],'logged' : 1 })  #not logged?




