import React from 'react'
import { Route, Link } from 'react-router-dom'

import axios from '../API'
import Layout from '../layout/NavBar'
import LeftNav from '../components/LeftNav'
import Entry from '../components/Entry'

export default class Home extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      entries: [],
      feeds: [],
      bookmarks: []
    }

    this.getEntries = this.getEntries.bind(this)
    this.postComment = this.postComment.bind(this)
    this.getBookmarks = this.getBookmarks.bind(this)
    this.toggleBookmark = this.toggleBookmark.bind(this)
    this.handleEntryClick = this.handleEntryClick.bind(this)
  }

  async componentDidMount() {
    let entries = []
    const feedUniqueName = this.props.match.params.feedUniqueName

    if (feedUniqueName) {
      let resp = await axios.get(`/feeds/?unique_name=${feedUniqueName}`)
      const feedId = resp.data.results[0].id
      const entriesResp = await axios.get(
        `/entries/?feed=${feedId}&order_by=-published_at`
      )
      entries = entriesResp.data.results.map(entry => ({
        ...entry,
        _feed_unique_name: feedUniqueName,
        _toggle: false
      }))
    }

    const feedsResp = await axios.get('/feeds/')
    const feeds = feedsResp.data.results

    let bookmarks = []
    if (this.props.location.pathname.startsWith('/bookmarks')) {
      const resp = await axios.get('/entries/?bookmarked=true')
      bookmarks = resp.data.results.map(entry => ({
        ...entry,
        _feed_unique_name: feedUniqueName,
        _toggle: false
      }))
    }

    this.setState({
      entries: entries,
      feeds: feeds,
      bookmarks: bookmarks
    })
  }

  async getBookmarks(event) {
    const resp = await axios.get('/entries/?bookmarked=true')
    const bookmarks = resp.data.results.map(entry => ({
      ...entry,
      _toggle: false
    }))

    this.setState({
      bookmarks: bookmarks
    })
  }

  async getEntries(event, feedId, feedUniqueName) {
    const entriesResp = await axios.get(
      `/entries/?feed=${feedId}&order_by=-published_at`
    )
    const entries = entriesResp.data.results.map(entry => ({
      ...entry,
      _feed_unique_name: feedUniqueName,
      _toggle: false
    }))

    this.setState({
      entries: entries
    })
  }

  async handleEntryClick(event, index, entryId) {
    const entries = [...this.state.entries]
    entries[index]._toggle = !entries[index]._toggle
    let feeds = this.state.feeds

    if (!this.state.entries[index].is_read) {
      await axios.post('/reads/', {entry: entryId})
      entries[index].is_read = true

      const feedIndex = this.state.feeds.findIndex(feed =>
        feed.id === this.state.entries[index].feed
      )
      feeds = [...this.state.feeds]
      feeds[feedIndex].unread_count -= 1
    }

    this.setState({
      entries: entries,
      feeds: feeds
    })
  }

  handleBookmarkClick(event, index, entryId) {
    const bookmarks = [...this.state.bookmarks]
    bookmarks[index]._toggle = !bookmarks[index]._toggle

    this.setState({
      bookmarks: bookmarks
    })
  } 

  async toggleBookmark(event, index, entryId) {
    if (!this.state.entries[index].is_bookmarked) {
      await axios.post('/bookmarks/', {entry: entryId})

      const entries = [...this.state.entries]
      entries[index].is_bookmarked = true
      this.setState({
        entries: entries
      })
    }
  }

  async postComment(entry, content) {
    if (!content) {
      return
    }
    const comment = {
      entry: entry.id,
      content: content
    }
    await axios.post('/comments/', comment)
    window.location.href = this.props.location.pathname
  }

  render() {
    const entries = this.state.entries.map((entry, index) =>
      <li style={{marginBottom: 5}} key={index}>
        <Entry
          href={`/feeds/${entry._feed_unique_name}/${entry.slug}`}
          entry={entry}
          handleEntryClick={event =>
              this.handleEntryClick(event, index, entry.id)
          }
          toggleBookmark={event =>
              this.toggleBookmark(event, index, entry.id)
          }
          toggle={this.state.entries[index]._toggle}
          postComment={content => this.postComment(entry, content)}
          isRead={entry.is_read}
        />
      </li>
    )

    const bookmarks = this.state.bookmarks.map((entry, index) =>
      <li style={{marginBottom: 5}} key={index}>
        <Entry
          href={`/bookmarks/${entry.slug}`}
          entry={entry}
          handleEntryClick={event =>
              this.handleBookmarkClick(event, index, entry.id)
          }
          toggleBookmark={event =>
              this.toggleBookmark(event, index, entry.id)
          }
          toggle={this.state.bookmarks[index]._toggle}
          postComment={content => this.postComment(entry, content)}
          isRead={entry.is_read}
        />
      </li>
    )

    const feeds = this.state.feeds.map((feed, index) =>
      <li key={index}>
        <Link
          to={`/feeds/${feed.unique_name}`}
          onClick={event => this.getEntries(event, feed.id, feed.unique_name)}
        >
          {`${feed.title} | (${feed.unread_count < 100 ? feed.unread_count : '+100'})`}
        </Link>
      </li>
    )

    return (
      <Layout>
        <div className="columns" style={{paddingTop: 20}}>
          <LeftNav feeds={feeds} bookmarks={this.getBookmarks} />
          <div className="column">
            <div style={{paddingRight: 20}}>
              <Route
                path="/feeds/:feed"
                render={props => <Entries {...props} entries={entries} />}
              />
              <Route
                path="/bookmarks"
                render={props => <Entries {...props} entries={bookmarks} />}
              />
            </div>
          </div>
        </div>
      </Layout>
    )
  }
}

function Entries(props) {
  return (
    <ul>
      {props.entries}
    </ul>
  )
}
