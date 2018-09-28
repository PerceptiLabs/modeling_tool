<template lang="pug">
  section.sidebar_comments
    .comments_head.sidebar-content.d-flex
      .comments_title.d-flex
        i.icon.icon-comments.big-text
        h3 Comments
        sup.comments-title_label New

      base-checkbox(labelPosition="left") Show on the workspace
    .comments_body(v-bar)
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
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }
  .comments_head {
    flex: 0 0 auto;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid $bg-toolbar;
    min-height: 3.8rem;
  }
  .comments_title {
    align-items: center;
    h3 {
      margin: 0 0 0 .25rem;
    }
  }
  .comments-title_label {
    background-color: $col-error;
    color: #fff;
    border-radius: 1em;
    padding: .75em .5em;
    font-weight: 300;
    top: -.9rem;
    font-size: .9rem;
  }
  .comments_body {
    flex: 1 1 100%;
    display: flex;
    flex-direction: column;
    > div {
      flex: 1 1 100%;
      overflow: auto;
    }
  }
  .comments-list,
  .user-comments_list {
    padding: 0;
    margin: 0;
    list-style: none;
    .right-btn {
      margin-left: auto;
    }
  }
  .user-comments {
    display: flex;
    align-items: center;
    border-bottom: 1px solid $bg-toolbar;
    height: $h-sidebar-layers-item;
    .btn {
      font-size: 1.2em;
    }
  }
  .user-comments_list {

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
    padding-top: .6em;
    padding-bottom: .6em;
    flex: 0 0 auto;
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
