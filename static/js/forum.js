document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('create-post-form');
  const postsContainer = document.getElementById('posts-container');
  const openModalBtn = document.getElementById('openCreatePostModal');
  const closeModalBtn = document.getElementById('closeCreatePostModal');
  const cancelBtn = document.getElementById('cancelCreatePost');
  const modal = document.getElementById('createPostModal');

  // --- Modal open/close ---
  function openModal() {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }

  function closeModal() {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }

  if (openModalBtn) openModalBtn.addEventListener('click', openModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  // --- Preview gambar ---
  const fileInput = document.querySelector('input[type="file"][name="image"]');
  const previewWrapper = document.getElementById('image-preview');
  const previewImg = document.getElementById('image-preview-img');

  if (fileInput) {
    fileInput.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (!file) {
        previewWrapper.classList.add('hidden');
        previewImg.src = '#';
        return;
      }
      const reader = new FileReader();
      reader.onload = function (ev) {
        previewImg.src = ev.target.result;
        previewWrapper.classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    });
  }

  // --- Submit form pakai AJAX ---
  if (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      const formData = new FormData(form);
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        postsContainer.insertAdjacentHTML('afterbegin', data.html);
        form.reset();

        // Reset preview juga
        previewWrapper.classList.add('hidden');
        previewImg.src = '#';

        // Animasi muncul halus
        const newPost = postsContainer.firstElementChild;
        newPost.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => {
          newPost.classList.remove('opacity-0', 'translate-y-2');
          newPost.classList.add('transition-all', 'duration-500');
        }, 50);

        closeModal();
      } else {
        console.error(data.errors);
        alert('Gagal membuat postingan!');
      }
    });
  }
});
