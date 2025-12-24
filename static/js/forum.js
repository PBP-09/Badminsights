document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('create-post-form');
  const postsContainer = document.getElementById('posts-container');
  const openModalBtn = document.getElementById('openCreatePostModal');
  const closeModalBtn = document.getElementById('closeCreatePostModal');
  const cancelBtn = document.getElementById('cancelCreatePost');
  const modal = document.getElementById('createPostModal');
  const totalCountEl = document.getElementById('total-posts-count');

  // simple toast
  function showToast(msg, type='success'){
    const t = document.createElement('div');
    t.className = `fixed top-5 right-5 px-4 py-2 rounded-lg z-50 ${type==='success' ? 'bg-green-500' : 'bg-red-500'} text-white`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=> { t.remove(); }, 2000);
  }

  function openModal(){ if(modal){ modal.classList.remove('hidden'); modal.classList.add('flex'); } }
  function closeModal(){ if(modal){ modal.classList.add('hidden'); modal.classList.remove('flex'); } }

  if (openModalBtn) openModalBtn.addEventListener('click', openModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', (e)=> { if (e.target === modal) closeModal(); });

  // helper: safe insert HTML (we only insert server-rendered fragment)
  function insertPostHTML(html){
    if(!postsContainer) return;
    postsContainer.insertAdjacentHTML('afterbegin', html);
    // animate appearance
    const newPost = postsContainer.firstElementChild;
    if(newPost){
      newPost.style.opacity = '0';
      newPost.style.transform = 'translateY(6px)';
      newPost.style.transition = 'all 300ms ease';
      requestAnimationFrame(()=> {
        newPost.style.opacity = '1';
        newPost.style.transform = 'translateY(0)';
      });
    }
  }

  // update total count
  function incTotalCount(){
    if(!totalCountEl) return;
    const n = parseInt(totalCountEl.textContent || '0', 10) || 0;
    totalCountEl.textContent = n + 1;
  }

  // show errors on form fields (basic)
  function showFormErrors(errors, formEl){
    // remove previous
    const old = formEl.querySelector('.ajax-errors');
    if(old) old.remove();

    const wrap = document.createElement('div');
    wrap.className = 'ajax-errors text-red-600 mb-3';
    for(const [k,v] of Object.entries(errors || {})){
      const row = document.createElement('div');
      row.textContent = `${k}: ${Array.isArray(v) ? v.join(', ') : v}`;
      wrap.appendChild(row);
    }
    formEl.prepend(wrap);
  }

  // === submit handler (delegated to support dynamic injection) ===
  document.addEventListener('submit', async function(e){
    if(!e.target.matches('#create-post-form')) return;
    e.preventDefault();
    const theForm = e.target;
    const fd = new FormData(theForm);

    // optional: disable submit button to prevent double submit
    const submitBtn = theForm.querySelector('button[type="submit"]');
    if(submitBtn) { submitBtn.disabled = true; submitBtn.classList.add('opacity-60'); }

    try{
      const res = await fetch(theForm.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': fd.get('csrfmiddlewaretoken') || '' // double-safety
        },
        body: fd,
        credentials: 'same-origin'
      });

      // 403 handling (CSRF) or other http errors
      if(res.status === 403){
        showToast('CSRF token missing/invalid (403)', 'error');
        console.error('CSRF or permission issue');
        return;
      }

      const data = await res.json();

      // tolerate both styles: data.status === 'success' OR data.success === true
      const ok = (data && (data.status === 'success' || data.success === true));

      if(ok){
        // if server sent rendered html fragment:
        if(data.html){
          insertPostHTML(data.html);
        } else if(data.post){
          // server returned raw data -> build minimal node client-side
          const html = buildPostHtmlFromData(data.post);
          insertPostHTML(html);
        }

        // update count, reset form & preview, close modal
        incTotalCount();
        theForm.reset();
        const previewWrapper = document.getElementById('image-preview');
        if(previewWrapper){ previewWrapper.classList.add('hidden'); }
        showToast(data.message || 'Postingan berhasil dibuat!');
        closeModal();
      } else {
        // show errors (server may return errors object or html_form)
        if(data.html_form){
          // replace form with returned form containing errors
          const modalBody = document.getElementById('createPostModal');
          if(modalBody){
            // find form container and replace inner HTML
            const inner = modalBody.querySelector('.p-6') || modalBody;
            inner.querySelector('form')?.remove();
            // put returned html_form inside modal
            const container = document.createElement('div');
            container.innerHTML = data.html_form;
            inner.appendChild(container);
          }
        } else if(data.errors){
          showFormErrors(data.errors, theForm);
        } else {
          showToast(data.message || 'Gagal membuat postingan', 'error');
          console.error('Unexpected response', data);
        }
      }

    } catch(err){
      console.error('Fetch error', err);
      showToast('Kesalahan jaringan. Coba lagi.', 'error');
    } finally {
      if(submitBtn){ submitBtn.disabled = false; submitBtn.classList.remove('opacity-60'); }
    }
  });

  // fallback: if server returns raw post JSON, build HTML here
  function buildPostHtmlFromData(post){
    // adjust classes to match your tailwind styles
    const snippet = `
      <article class="bg-white rounded-xl shadow-sm overflow-hidden">
        <div class="p-5">
          <div class="flex justify-between items-start gap-4">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900">
                <a href="/forum/post/${post.id}/" class="hover:underline">${escapeHtml(post.title)}</a>
              </h3>
              <div class="mt-2 inline-flex items-center gap-2">
                <span class="px-2 py-1 rounded-md text-xs font-semibold text-white bg-blue-600">${escapeHtml(post.category || '')}</span>
                <span class="text-sm text-gray-500">${escapeHtml(post.author || '')}</span>
                <span class="text-sm text-gray-400">•</span>
                <time class="text-sm text-gray-400">${escapeHtml(post.created_at || '')}</time>
              </div>
            </div>
            <div class="text-right text-sm text-gray-500 whitespace-nowrap">
              <div>👍 <span class="font-semibold text-gray-700">0</span></div>
              <div class="mt-1">💬 <span class="font-semibold text-gray-700">0</span></div>
            </div>
          </div>
          <p class="mt-4 text-gray-700">${escapeHtml(truncate(post.content || '', 30))}</p>
        </div>
      </article>
    `;
    return snippet;
  }

  function truncate(s, words){
    return s.split(/\s+/).slice(0, words).join(' ');
  }

  function escapeHtml(unsafe){
    return String(unsafe)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }
});
