import React from 'react'
import { Route, Link } from 'react-router-dom'
import moment from 'moment'

import { Comment, CommentInput } from './Comment'

export default function Entry(props) {
  return (
    <div className="card">
      <div className={['card-header',
        props.isRead ? 'has-background-grey-lighter' : ''].join(' ')}>
        <Link
          to={props.href}
          className="card-header-title"
          onClick={props.handleEntryClick}
        >
          {props.entry.title}
        </Link>
      </div>
      {
        props.toggle
          &&
          <div className="card-content">
            <h5 className="title is-5">
              <a href={props.entry.link}>{props.entry.title}</a>
            </h5>
            <h6 className="subtitle is-size-7">
              Published on {moment(props.entry.published_at).format('MMM D [at] HH:mma')}
            </h6>
            <div
              className="content"
              dangerouslySetInnerHTML={{__html: props.entry.summary}}
            >
            </div>
            <button
              className={['button',
                props.entry.is_bookmarked ? 'is-static' : ''].join(' ')}
              onClick={props.toggleBookmark}
            >
              {props.entry.is_bookmarked ? 'Bookmarked' : 'Bookmark'}
            </button>
            <br />
            <hr />
            <Route
              path="/feeds/:feed/:slug"
              render={attrs => <Comment {...attrs} entryId={props.entry.id} />}
            />
            <Route
              path="/bookmarks"
              render={attrs => <Comment {...attrs} entryId={props.entry.id} />}
            />
            <CommentInput callback={props.postComment} />
        </div>
      }
    </div>
  )
}
