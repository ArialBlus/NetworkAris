from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import json
from django.http import JsonResponse

from .models import User, Post, Follow, Like, Comment

from django.db.models import Count
from django.template.loader import render_to_string



from django.db.models import Count

def index(request):
    # Obtén todos los posts y configura la paginación
    allPosts = Post.objects.all().annotate(like_count=Count('post')).order_by("-date")
    
    paginator = Paginator(allPosts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Extraer los IDs de los posts de la página actual
    post_ids = list(page_obj.object_list.values_list('id', flat=True))
    posts_html = render_to_string('network/posts_list.html', {'page_obj': page_obj}, request=request)
    

    # Verifica si el usuario está autenticado y obtiene sus likes
    user_likes = set()  # Usar un set para evitar duplicados
    if request.user.is_authenticated:
        user_likes = {like.post.id for like in Like.objects.filter(user=request.user)}
        #Todos los ikes guardados por ende son css dislike

    if request.is_ajax():
    # Verificar que 'posts_html' no esté vacío
        return JsonResponse({
            'posts_html': posts_html, # Texto en lugar de HTML vacío
            'has_next': page_obj.has_next(),
            'user_likes': list(user_likes),
        })
        


    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "postYouLike": list(user_likes),
        'posts_html': posts_html,
        'has_next': page_obj.has_next(),
    })



def comment_post(request, post_id):
    # Obtén el post solicitado o lanza un error 404 si no existe
    post = get_object_or_404(Post, id=post_id)
    
    # Filtra los comentarios relacionados con este post
    comments = Comment.objects.filter(post=post)  # Ordenados por fecha, si tienes un campo 'created_at'
    
    # Renderiza la plantilla con los datos
    return render(request, 'network/comment.html', {
        'post': post,
        'comments': comments,  # Solo los comentarios relacionados con este post
    })  

def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image', None)
        post = Post.objects.get(id=post_id)

        # Crear un nuevo comentario
        comment = Comment(content=content, user=request.user, post=post, image=image)
        comment.save()

        # Devolver los datos del nuevo comentario
        response_data = {
            'content': comment.content,
            'user': comment.user.username,
        }

        # Si hay una imagen, agregar la URL de la imagen
        if comment.image:
            response_data['image_url'] = comment.image.url

        return JsonResponse(response_data)

    return redirect('post_comments', post_id=post_id)






@csrf_exempt  # Esto es inseguro en producción; asegúrate de manejar CSRF adecuadamente
@csrf_exempt
def likePost(request, post_id):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        # Verifica si ya existe un Like
        like, created = Like.objects.get_or_create(user=user, post=post)

        if created:
            # Si se creó un nuevo Like
            like_count = Like.objects.filter(post=post).count()
            return JsonResponse({"message": "Post liked successfully!", "like_count": like_count}, status=200)
        else:
            # Si ya existía el Like, no envíes un error
            like_count = Like.objects.filter(post=post).count()
            return JsonResponse({"message": "You already liked this post", "like_count": like_count}, status=200)
    
    return JsonResponse({"error": "Bad request"}, status=400)


@csrf_exempt
@csrf_exempt
def unLikePost(request, post_id):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        # Busca y elimina el Like si existe
        like = Like.objects.filter(user=user, post=post).first()
        if like:
            like.delete()
            like_count = Like.objects.filter(post=post).count()
            return JsonResponse({"message": "Post disliked successfully!", "like_count": like_count}, status=200)
        else:
            # Si no existe un Like, no envíes un error
            like_count = Like.objects.filter(post=post).count()
            return JsonResponse({"message": "You haven't liked this post yet", "like_count": like_count}, status=200)
    
    return JsonResponse({"error": "Bad request"}, status=400)

       




def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPosts = Post.objects.filter(user=user).order_by("id").reverse()

    paginator = Paginator(allPosts, 4)  # 5 publicaciones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Usuarios que siguen al perfil y usuarios que el perfil sigue
    followers = Follow.objects.filter(userFollowing=user)
    following = Follow.objects.filter(user=user)

    is_owner = request.user.id == user_id  # Verifica si el usuario autenticado es el dueño del perfil


    # Verificar si el usuario actual está siguiendo al usuario del perfil
    isFollowing = False
    if request.user.is_authenticated:
        isFollowing = followers.filter(user=request.user).exists()

    user_likes = set() 
    if request.user.is_authenticated:
        user_likes = {like.post.id for like in Like.objects.filter(user=request.user)}
       

    # Renderizar los posts en formato HTML para AJAX

   
    posts_html = render_to_string('network/posts_list.html', {'page_obj': page_obj, 'is_owner': is_owner}, request=request)

 
    if request.is_ajax():
    # Verificar que 'posts_html' no esté vacío
        return JsonResponse({
            'posts_html': posts_html, # Texto en lugar de HTML vacío
            'has_next': page_obj.has_next(),
            'user_likes': list(user_likes),
            'is_owner': is_owner,
        })

    return render(request, "network/profile.html", {
        "page_obj": page_obj,
        "following": following,
        "followers": followers,
        "Username": user,
        "isFollowing": isFollowing,
        "profile_user": user,
        "is_owner": is_owner,  # Asegúrate de pasar is_owner al contexto

    })





def edit(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=id)
            data = json.loads(request.body)
            post.content = data["content"]
            post.save()
            # Respuesta en formato JSON para la solicitud AJAX
            return JsonResponse({"message": "Post actualizado exitosamente"}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({"error": "El post no existe"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

        
   


def following(request):
    currentUser = User.objects.get(pk=request.user.id)

    # Obtener los usuarios que el perfil sigue
    followingPeople = Follow.objects.filter(user=currentUser)  # Usuarios que el perfil sigue

    
    allPost = Post.objects.all().order_by("id").reverse()
    followingPosts = []

    for follow in followingPeople:
        followingPosts.append(follow.userFollowing)
    
    
    # Ahora obtén las publicaciones de esos usuarios
    postsFromFollowing = Post.objects.filter(user__in=followingPosts).order_by('-id')


    #followingPosts = Post.objects.filter(user__in=followingPeople).order_by('-id')

    paginator = Paginator(postsFromFollowing, 5)  # 5 publicaciones por página
    
    # Obtener el número de la página de la solicitud GET
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, "network/following.html", {
        "allPost": allPost,
        "page_obj": page_obj
    })

 

def follow(request):
    currentUser = User.objects.get(pk=request.user.id)
    userFollow = request.POST["userFollow"]
    
    # Intentar obtener el usuario a seguir
    
    userFollowData = User.objects.get(username=userFollow)
   
    # Verificar si la relación de seguimiento ya existe para evitar duplicados
    if not Follow.objects.filter(user=currentUser, userFollowing=userFollowData).exists():
        # Crear la relación de seguimiento solo si no existe
        J = Follow(user=currentUser, userFollowing=userFollowData)
        J.save()

    #      try:
    #     J = Follow.objects.get(user=currentUser, userFollowing=userFollowData)
    #     J.delete()
    # except Follow.DoesNotExist:
    #     # Manejar el caso si la relación no existe
    #     pass


    return HttpResponseRedirect(reverse('profile', args=[userFollowData.id]))


def unFollow(request):
    if request.method == "POST":
        currentUser = User.objects.get(pk=request.user.id)
        userFollow = request.POST["userFollow"]
        
        # Intentar obtener el usuario a dejar de seguir
    
        userFollowData = User.objects.get(username=userFollow)
       
        
        # Buscar la relación de seguimiento existente y eliminarla
        try:
            # Obtener la relación que existe y eliminarla
            J = Follow.objects.get(user=currentUser, userFollowing=userFollowData)
            J.delete()
        except Follow.DoesNotExist:
            # Manejar el caso donde la relación no existe (quizás ya ha sido eliminada)
            pass
        
        return HttpResponseRedirect(reverse('profile', args=[userFollowData.id]))


#@login_required
#@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Verificar si el usuario es el propietario del post
    if post.user == request.user:
        post.delete()
    else:
        return redirect('profile', user_id=request.user.id)  # Redirigir al perfil del usuario

    # Redirigir al perfil después de eliminar el post
    return redirect('profile', user_id=request.user.id)  # Asegúrate de incluir el user_id

   

def newPost(request):
    if request.method == "POST":
        content = request.POST.get('content')
        image = request.FILES.get('image')
        post = Post(content=content, user=request.user, image=image)
        post.save()
        return HttpResponseRedirect(reverse('index'))   
    
    



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
