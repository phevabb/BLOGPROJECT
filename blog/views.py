from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.shortcuts import render
from .forms import SearchForm
from .models import Post
from django.db.models import Q

from django.contrib.postgres.search import (
SearchVector,
SearchQuery,
SearchRank
)


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Perform simple search using icontains (case-insensitive partial match)
            results = Post.published.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            ).distinct()

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)


    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return render(request, 'blog/post/comment_added_success.html', {'post': post, 'form': form, 'comment': comment})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri( post.get_absolute_url() )

            # subject
            subject = (
                f"{cd['name']} ({cd['email']})"
                f"recommends you read {post.title}"
            )

            # message
            message= (
                f"read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments:{cd['comments']}"
            )

            # send mail
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
            return render(request, 'blog/post/share.html', {'sent':sent, 'form': form, 'post': post})
    else:
        form = EmailPostForm()
        return render(request, 'blog/post/share.html', {'form': form, 'post':post, 'sent': sent})




def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:

        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

def post_detail(request, id):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    comments = post.comment_post_ship.filter(active=True)
    num_of_comments = comments.count()
    form = CommentForm()

    # LIST OF SIMILAR POSTS
    # assumings the id that came in the request is 1. and has title, body works. with these tags[jazz, food, cars, education]
    # and the tags also has ids of 2, 3, 5, 7 respectively, then ids of the tags will be stored in post_tags_ids
    post_tags_ids = post.tags.all().values_list('id', flat=True)



    # we search through the entire Post model and filter the Post objects whose tag ids are similar to the ones found. we exclude the original post id.
    # similar_post will hold all published objects whose tag field values are equal to [2, 3, 5, 7]
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)

    # we create a new field for each post object called same_tags
    # the number of items in the tag field of the similar_posts queryset are counted and placed in a new field called same_tags
    # remember the tags in the original object (object whose request came to the view) is [jazz, food, cars, education]
    # assuming the is a post object with tags [ food, cars, fashion,]
    # then its same_tag field would be 2 since fashion cant be found in the original object.
    # The -same_tags orders the posts by the number of shared tags in descending order (most shared tags first).
    # If two posts have the same number of shared tags, the -publish orders them by their publish date in descending order (most recent first).
    # [:4]:  This slicing operation limits the queryset to the top 4 posts after the ordering is applied
    similar_posts= similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,'similar_posts': similar_posts, 'form': form, 'comments': comments, 'num_of_comments': num_of_comments})





# Create your views here.
