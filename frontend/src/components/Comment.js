import React from 'react'

import axios from '../API'

export class Comment extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      comments: []
    }
  }

  async componentDidMount() {
    const comments = await axios.get(`/comments/?entry=${this.props.entryId}`)
    this.setState({
      comments: comments.data.results
    })
  }

  render() {
    const comments = this.state.comments.map((comment, index) => (
      <div className="media" key={index}>
        <div className="media-left">
          <p className="image is-64x64">
            <img alt="" src="https://bulma.io/images/placeholders/128x128.png" />
          </p>
        </div>
        <div className="media-content">
          <div className="content">
            <p>
              <strong>
                {comment.author.username}
              </strong>
              <br />
              {comment.content}
              <br />
            </p>
          </div>
        </div>
      </div>
    ))

    return (
      <React.Fragment>
        {comments}
      </React.Fragment>
    )
  }
}

export class CommentInput extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      content: ''
    }

    this.handleChange = this.handleChange.bind(this)
    this.postComment = this.postComment.bind(this)
  }

  handleChange(event) {
    this.setState({content: event.target.value})
  }

  postComment() {
    if (!this.state.content) {
      return
    }
    this.props.callback(this.state.content)
    this.setState({
      content: ''
    })
  }

  render() {
    return (
      <div className="media">
        <div className="media-left">
          <p className="image is-64x64">
            <img alt="" src="https://bulma.io/images/placeholders/128x128.png" />
          </p>
        </div>
        <div className="media-content">
          <div className="field">
            <p className="control">
              <textarea
                className="textarea"
                placeholder="Add a comment..."
                value={this.state.content}
                onChange={this.handleChange}
              />
            </p>
          </div>
          <div className="field">
            <p className="control">
              <button
                className="button"
                onClick={this.postComment}
              >
                Post comment
              </button>
            </p>
          </div>
        </div>
      </div>
    )
  }
}
