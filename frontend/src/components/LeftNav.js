import React from 'react'
import { Link } from 'react-router-dom'

export default function LeftNav(props) {
  return (
    <div className="column is-one-fifth">
      <div className="menu" style={{paddingLeft: 20}}>
        <p className="menu-label">
          General
        </p>
        <ul className="menu-list">
          <li>
            <Link
              to="/bookmarks"
              onClick={props.bookmarks}
            >
              Bookmarks
            </Link>
          </li>
        </ul>
        <p className="menu-label">Feeds</p>
        <ul className="menu-list">
          {props.feeds}
        </ul>
      </div>
    </div>
  )
}
