<template lang="pug">
  section.sidebar_comments
    .comments_head.sidebar-content.d-flex
      .comments_title.d-flex
        i.icon.icon-comments
        h4 Comments

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
              )
                .user-comment_meta
                  span
                    i.icon.icon-comments
                    | {{ comment.time }}
                  button.btn.btn--icon.right-btn(type="button")
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
              text: 'Remove the input_2',
              time: '5 min ago',
            },
            {
              text: 'Remove the input',
              time: '5 min ago',
            }
          ]
        }, {
          userName: 'Smith John',
          isOpen: false,
          comments: [
            {
              text: 'Add the input_2 Add the input_2 Add the input_2 Add the input_2 Add the input_2Add the input_2 Add the input_2',
              time: '5 min ago',
            },
            {
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
  .sidebar-content {
    padding-top: 10px;
    padding-bottom: 10px;
  }
  .sidebar_comments {
    display: flex;
    flex-direction: column;

  }
  .comments_head {
    flex: 0 0 auto;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid $bg-toolbar;
  }
  .comments_title {
    align-items: center;
    h4 {
      margin: 0 0 0 .5em;
    }
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
  }
  .user-comments_list {

  }
  .user-comment {
    padding-left: 2em;
    border-bottom: 1px solid $bg-toolbar;
  }
  .user-comment_meta {
    display: flex;
    align-items: center;
  }
  .user-comment_text {

  }
  .comments_meta {
    padding-top: .5em;
    padding-bottom: .5em;
    flex: 0 0 auto;
    border-top: 1px solid $bg-toolbar;
  }
  .comments_actions {
    text-align: right;
  }
</style>
