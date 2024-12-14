document.addEventListener("DOMContentLoaded", () => {
    let currentPage = 1; // Página actual
    let loading = false; // Bandera para evitar múltiples llamadas
    const postContainer = document.querySelector(".post-container"); // Contenedor de posts
    const existingPostIds = new Set(); // Controlar posts únicos

    const modal = document.getElementById("globalModal");
    const textarea = document.getElementById("globalTextarea");
    let currentPostId = null;

    // Asignar el evento de scroll infinito
    window.addEventListener("scroll", () => {
        if (loading) return;

        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
            loading = true; // Bloquear múltiples llamadas
            loadMorePosts();
        }
    });

    function loadMorePosts() {
        currentPage += 1;

        fetch(`?page=${currentPage}`, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then(response => {
                if (!response.ok) throw new Error("Error al cargar más posts");
                return response.json();
            })
            .then(data => {
                if (data.posts_html) {
                    const tempDiv = document.createElement("div");
                    tempDiv.innerHTML = data.posts_html;

                    const newPosts = tempDiv.querySelectorAll(".card");
                    newPosts.forEach(post => {
                        const postId = post.id.split("-")[1];
                        if (!existingPostIds.has(postId)) {
                            existingPostIds.add(postId);
                            postContainer.insertAdjacentHTML("beforeend", post.outerHTML);
                        }
                    });
                    

                    // Inicializar eventos después de agregar los nuevos posts
                    initializePostEvents();
                }
                loading = false;
            })
            .catch(error => {
                console.error("Error al cargar más posts:", error);
                loading = false;
            });
    }

    
    function initializePostEvents() {
        
        console.log("Reinicializando eventos para los posts.");

        // Botón de abrir modal
        try {
            document.querySelectorAll(".open-modal-btn").forEach(button => {
                button.addEventListener("click", event => {
                    try {
                        // Obtener el modal y el textarea
                        const modal = document.querySelector("#globalModal");
                        const textarea = document.querySelector("#globalTextarea");
        
                        if (!modal) {
                            console.error("No se encontró el modal con el ID '#globalModal'.");
                            return;
                        }
        
                        if (!textarea) {
                            console.error("No se encontró el textarea con el ID '#globalTextarea'.");
                            return;
                        }
        
                        // Obtener el ID del post actual y su contenido
                        currentPostId = button.getAttribute("data-post-id");
                        const postContentElement = document.getElementById(`post-content-${currentPostId}`);
                        
                        if (!postContentElement) {
                            console.error(`No se encontró el contenido del post con el ID 'post-content-${currentPostId}'.`);
                            return;
                        }
        
                        const postContent = postContentElement.textContent;
        
                        // Establecer el contenido del textarea
                        textarea.value = postContent;
        
                        // Asegurar que el scroll esté al inicio
                        
        
                        // Abrir el modal
                        modal.style.display = "flex";
                        modal.classList.add("show");
                        document.body.style.overflow = "hidden";
                    } catch (innerError) {
                        console.error("Error al abrir el modal:", innerError);
                    }
                });
            });
        } catch (error) {
            console.error("Error al configurar los botones de apertura de modal:", error);
        }
        

        // Botón de cerrar modal
        document.querySelectorAll(".close-modal-btn").forEach(button => {
            button.addEventListener("click", () => {
                modal.style.display = "none";
                modal.classList.remove("show");
                document.body.style.overflow = "auto";
            });
        });

        // Botón de guardar cambios
        // Botón de guardar cambios
        document.addEventListener("click", (event) => {
            if (event.target.matches(".save-changes-btn")) {
                if (!currentPostId) return;
        
                const newContent = textarea.value;
        
                fetch(`/edit/${currentPostId}`, {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: JSON.stringify({ content: newContent }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // Actualiza el contenido del post con el enlace correcto
                        const postElement = document.getElementById(`post-content-${currentPostId}`);
                        postElement.innerHTML = `
                            <p id="post-content-${currentPostId}" class="card-text">
                                <a href="/post/${currentPostId}/comments/" class="post-link" data-post-id="${currentPostId}">
                                    ${newContent}
                                </a>
                            </p>
                        `;
        
                        modal.style.display = "none";
                        modal.classList.remove("show");
                        document.body.style.overflow = "auto";
                    } else if (data.error) {
                        console.error('Error del servidor:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error al guardar los cambios:', error);
                });
            }
        });
        
                
        

        // Botones de like y dislike
        document.querySelectorAll(".like-button").forEach(button => {
            button.addEventListener("click", () => {
                const postId = button.id.split("-")[2];
                likeHandler(postId);
            });
        });
    }


    // Lógica de Like / Dislike
    function likeHandler(id) {
        const btn = document.getElementById(`like-button-${id}`);
        const likeCountElem = document.getElementById(`like-count-${id}`);
    
        if (!btn || !likeCountElem) {
            console.error(`Element not found for post ID: ${id}`);
            return;
        }
    
        const liked = btn.getAttribute("data-liked") === "true";
        const url = liked ? `/unLikePost/${id}/` : `/likePost/${id}/`;
    
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then((data) => {
                        throw new Error(data.error || "Error en la solicitud");
                    });
                }
                return response.json();
            })
            .then((result) => {
                console.log(result.message);
    
                // Actualiza el estado del botón y contador de likes
                btn.classList.toggle("btn-danger", !liked);
                btn.classList.toggle("btn-primary", liked);
                btn.innerHTML = liked
                    ? '<i class="bi bi-hand-thumbs-up"></i> Like'
                    : '<i class="bi bi-hand-thumbs-down"></i> Dislike';
                btn.setAttribute("data-liked", liked ? "false" : "true");
    
                // Usa el valor de la respuesta del servidor
                likeCountElem.innerText = result.like_count;
            })
            .catch((error) => console.error("Error en like/unlike:", error));
    }
    

    
    function previewImage(event) {
        const imagePreviewContainer = document.getElementById("imagePreviewContainer");
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            imagePreviewContainer.innerHTML = '';  // Limpia cualquier vista previa anterior
            const img = document.createElement("img");
            img.src = e.target.result;
            img.classList.add("preview-image");
            imagePreviewContainer.appendChild(img);  // Añade la imagen fuera del contenido editable
            adjustDivHeight();
        };
        reader.readAsDataURL(file);
    }

    

    function adjustDivHeight() {
        const contentDiv = document.getElementById("postContent");

        // Solo aumentar la altura si el contenido supera el tamaño actual
        if (contentDiv.scrollHeight > contentDiv.clientHeight) {
            contentDiv.style.height = `${contentDiv.scrollHeight}px`;
        }
    }

    function handleImageSubmit() {
        const contentDiv = document.getElementById("postContent");
        const contentInput = document.getElementById("contentInput");
        
        // Copia solo el texto de postContent al campo oculto antes de enviar el formulario
        contentInput.value = contentDiv.innerText;  // Usamos innerText para evitar el HTML de la imagen
        
        return true; // Permite el envío del formulario
    }

    function syncContentEditableToInput() {
        const postContent = document.getElementById('postContent').innerHTML.trim(); // Obtén el contenido del div
        const contentInput = document.getElementById('contentInput'); // Campo oculto
        contentInput.value = postContent; // Copia el contenido al input oculto
    }
    
    // Llamar a la inicialización al cargar la página
    initializePostEvents();

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return null;
    }
    

    //METODO AGREGAR UN COMENTARIO: 
    
    


    // Exponer funciones para uso global (si es necesario)
    window.likeHandler = likeHandler;
    window.previewImage = previewImage;
    window.handleImageSubmit = handleImageSubmit;
    window.adjustDivHeight = adjustDivHeight;
  
    
    
    
    
});
