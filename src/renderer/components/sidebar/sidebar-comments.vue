<template lang="pug">
  section.sidebar_comments
    .comments_head.sidebar-content.d-flex
      .comments_title.d-flex
        i.icon.icon-comments.big-text
        h3 Comments
        sup.comments-title_label New

      base-checkbox(labelPosition="left") Show on the workspace
    .comments_body
      div
        ul.comments-list
          li(
            v-for="(user, i) in commentsList"
            :key="i"
          )
            .user-comments.sidebar-content
              button.btn.btn--icon(type="button")
                i.icon.icon-empty
              button.btn.btn--icon(type="button")
                i.icon.icon-shevron
              span {{ user.userName }}
              button.btn.btn--icon.right-btn(type="button")
                i.icon.icon-menu
            ul.user-comments_list
              li.user-comment(
                v-for="(comment, i) in user.comments"
                :key="i"
                :class="{'text-disable': !comment.isResolve}"
              )
                .user-comment_meta
                  time.comment-meta_time.small-text
                    i.icon.icon-comments.big-text
                    | {{ comment.time }}
                  button.btn.btn--icon.right-btn.text-default(type="button")
                    i.icon.icon-menu
                .user-comment_text {{ comment.text }}
    .comments_meta.sidebar-content
      .comments_actions
        button.btn.btn--icon(type="button") Leave the comment
          i.icon.icon-comments

</template>

<script>
export default {
  name: 'SidebarComments',
  data() {
    return {
      commentsList: [
        {
          userName: 'John Smith',
          isOpen: false,
          comments: [
            {
              isResolve: true,
              text: 'Remove the input_2',
              time: '5 min ago',
            },
            {
              isResolve: false,
              text: 'Remove the input',
              time: '5 min ago',
            }
          ]
        }, {
          userName: 'Smith John',
          isOpen: false,
          comments: [
            {
              isResolve: true,
              text: 'Add the input_2 Add the input_2 Add the input_2 Add the input_2 Add the input_2Add the input_2 Add the input_2',
              time: '5 min ago',
            },
            {
              isResolve: true,
              text: 'Add the input',
              time: '5 min ago',
            }
          ]
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar_comments {
    display: flex;
    overflow: hidden;
    flex: 1;
    flex-direction: column;
  }
  .comments_head {
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;
    min-height: 3.8rem;
    border-bottom: 1px solid $bg-toolbar;
  }
  .comments_title {
    align-items: center;
    h3 {
      margin: 0 0 0 .25rem;
    }
  }
  .comments-title_label {
    font-size: .9rem;
    font-weight: 300;
    color: #fff;
    top: -.9rem;
    padding: .75em .5em;
    border-radius: 1em;
    background-color: $col-error;
  }
  .comments_body {
    display: flex;
    flex: 1 1 100%;
    flex-direction: column;
    > div {
      overflow: auto;
      flex: 1 1 100%;
    }
  }
  .comments-list,
  .user-comments_list {
    margin: 0;
    padding: 0;
    list-style: none;
    .right-btn {
      margin-left: auto;
    }
  }
  .user-comments {
    display: flex;
    align-items: center;
    height: $h-sidebar-layers-item;
    border-bottom: 1px solid $bg-toolbar;
    .btn {
      font-size: 1.2em;
    }
  }

  .user-comment {
    padding: .8rem $h-sidebar-layers-indent .8rem 4rem;
    border-bottom: 1px solid $bg-toolbar;
  }
  .user-comment_meta {
    display: flex;
    align-items: center;
    margin-bottom: .5rem;
  }
  .comment-meta_time {
    display: flex;
    align-items: center;
    .icon {
      margin-right: .25em;
    }
  }
  .user-comment_text {
    padding-left: 2em;
  }
  .comments_meta {
    flex: 0 0 auto;
    padding-top: .6em;
    padding-bottom: .6em;
    border-top: 1px solid $bg-toolbar;
  }
  .comments_actions {
    .btn {
      display: flex;
      align-items: center;
      margin-left: auto;
      .icon {
        font-size: 1.5em;
        margin-left: 1em;
      }
    }
  }

</style>
