function getGraphQLUrl() {
    return sessionStorage.getItem('graphQlUrl')
}
const setInnerHTML = (elm, html) => {
    elm.innerHTML = html
    Array.from(elm.querySelectorAll('script')).forEach(function (oldScript) {
        const newScript = document.createElement('script')
        Array.from(oldScript.attributes).forEach(function (attr) {
            return newScript.setAttribute(attr.name, attr.value)
        })
        newScript.appendChild(document.createTextNode(oldScript.innerHTML))
        oldScript.parentNode.replaceChild(newScript, oldScript)
    })
    return elm
}
const setResourceWidgetHTML = (elm, html) => {
    const documentContent = new DOMParser().parseFromString(html, 'text/html')
    documentContent.querySelectorAll('script, style').forEach((element) => element.remove())
    documentContent.querySelectorAll('a').forEach((link) => {
        const downloadResourceId = link
            .getAttribute('onclick')
            ?.match(/setResourceDownloadableLink\(event,\s*["']([^"']+)["'],\s*false\)/)?.[1]
        if (downloadResourceId) {
            link.setAttribute('data-resource-download-id', downloadResourceId)
            link.setAttribute('href', '#')
        }
    })
    documentContent.querySelectorAll('*').forEach((element) => {
        Array.from(element.attributes).forEach((attribute) => {
            if (attribute.name.toLowerCase().startsWith('on')) {
                element.removeAttribute(attribute.name)
            }
        })
    })
    elm.innerHTML = documentContent.body.innerHTML
    elm.querySelectorAll('[data-resource-download-id]').forEach((link) => {
        link.addEventListener('click', async (event) => {
            event.preventDefault()
            if (link.hasAttribute('disabled')) return

            const resourceId = link.getAttribute('data-resource-download-id')
            if (!resourceId) return

            const uri = await getDownloadableLinkAndDownloadResource(resourceId, false)
            if (!uri) return

            const downloadLink = document.createElement('a')
            downloadLink.href = uri
            downloadLink.download = ''
            downloadLink.target = '_blank'
            document.body.appendChild(downloadLink)
            downloadLink.click()
            downloadLink.remove()
        })
    })
    return elm
}
const fetchDataAndSetInnerHTML = async (id, element, queryBody, operationName) => {
    let cont = '<div id=' + id + '>'
    if (typeof queryBody === 'string') {
        queryBody = JSON.parse(queryBody)
    }
    let endpoint = getGraphQLUrl()
    const token = localStorage.getItem('AuthToken')
    const headers = {
        orgName: sessionStorage.getItem('orgName'),
        'Content-Type': 'application/json',
        'Accept-Language': localStorage.getItem('i18nextLng'),
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }
    return fetch(endpoint, {
        headers,
        body: queryBody.body,
        method: 'POST',
    })
        .then(function (res) {
            return res.json()
        })
        .then(function (res) {
            cont += res.data[operationName] + '</div>'
            return setInnerHTML(element, cont)
        })
}
const fetchResourceWidgetData = (queryBody) => {
    const endpoint = getGraphQLUrl()
    const token = localStorage.getItem('AuthToken')
    const headers = {
        orgName: sessionStorage.getItem('orgName'),
        'Content-Type': 'application/json',
        'Accept-Language': localStorage.getItem('i18nextLng'),
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }
    return fetch(endpoint, {
        headers,
        body: queryBody.body,
        method: 'POST',
    }).then((response) => response.json())
}
const initializeResourceWidgets = (container, html) => {
    if (!container || !html) return

    const documentContent = new DOMParser().parseFromString(html, 'text/html')
    documentContent.querySelectorAll('script').forEach((script) => {
        const scriptContent = script.textContent || ''
        const targetId = scriptContent.match(/fetchDataAndSetInnerHTML\(\s*["']([^"']+)["']/)?.[1]
        const rawBody = scriptContent.match(/body\s*:\s*'([^']+)'/)?.[1]
        if (!targetId || !rawBody || !scriptContent.includes('"resourceWidget"')) return

        try {
            const element = container.querySelector(`[id="${targetId}"]`)
            const queryBody = { body: rawBody.replace(/\\\\/g, '\\').replace(/\\'/g, "'") }
            if (!element) return

            fetchResourceWidgetData(queryBody).then((response) => {
                setResourceWidgetHTML(element, response?.data?.resourceWidget || '')
            })
        } catch (error) {
            console.error('Unable to initialize resource widget', error)
        }
    })
}
window.initializeResourceWidgets = initializeResourceWidgets
const getPage = (event, locale) => {
    event.preventDefault()
    if (locale === localStorage['i18nextLng']) return
    let loader = document.getElementById('loaderDiv')
    loader.style.display = 'block'
    let url = localStorage['currentPageUrl'] + '/' + locale + '.html'
    fetch(url)
        .then(function (res) {
            return res.text()
        })
        .then(function (res) {
            let _a, _b
            loader.style.display = 'none'
            if (res.includes('Access Denied')) {
                alert('Page is not available in ' + locale)
                ;(_a = document.getElementById('languageDropdown')) === null || _a === void 0
                    ? void 0
                    : _a.classList.toggle('active')
                return
            }
            setInnerHTML(document.body, res)
            localStorage['i18nextLng'] = locale
            ;(_b = document.getElementById(locale + '_selector')) === null || _b === void 0
                ? void 0
                : _b.classList.add('selected')
        })
}
const showLanguageDropdown = () => {
    let dropdown = document.getElementById('languageDropdown')
    dropdown === null || dropdown === void 0 ? void 0 : dropdown.classList.toggle('active')
}

const getResource = (resourceUuid) => {
    let query = `query lorResourceDownloadableLink($id: String){lorResourceDownloadableLink(id: $id)}`
    return {
        body: JSON.stringify({
            operationName: 'lorResourceDownloadableLink',
            query,
            variables: { id: resourceUuid },
        }),
    }
}

const getResourceLocationDownload = (resourceUuid) => {
    let query = `query getResourceLocationDownload($resourceId: ID!) {\n  getResourceLocationDownload(resourceId: $resourceId)\n}\n`
    return {
        body: JSON.stringify({
            operationName: 'getResourceLocationDownload',
            query,
            variables: { resourceId: resourceUuid },
        }),
    }
}

const getDownloadableLinkAndDownloadResource = async (id, lorResource = true) => {
    const GRAPHQL_URL = sessionStorage.getItem('graphQlUrl')
    const token = localStorage.getItem('AuthToken')
    const headers = {
        orgName: sessionStorage.getItem('orgName'),
        'Content-Type': 'application/json',
        'Accept-Language': localStorage.getItem('i18nextLng'),
    }
    let body, propertyName
    if (token && token != 'null') {
        headers['Authorization'] = `Bearer ${token}`
    }
    if (lorResource) {
        body = getResource(id).body
        propertyName = 'lorResourceDownloadableLink'
    } else {
        body = getResourceLocationDownload(id).body
        propertyName = 'getResourceLocationDownload'
    }
    return fetch(GRAPHQL_URL, {
        headers,
        body: body,
        method: 'POST',
    })
        .then((res) => res.json())
        .then((res) => {
            return res?.data?.[propertyName]
        })
        .catch((err) => {
            console.error(
                'Something went wrong while fetching the downloadable link name / uuid' +
                    id +
                    'and the reason is' +
                    err,
            )
        })
}

if (window.setDownloadableLink === undefined) {
    window.setDownloadableLink = async (event, id) => {
        let target = event.target
        if (event.target.nodeName !== 'A') {
            target = event.target.parentElement
        }
        if (target.getAttribute('href') == '') {
            event.preventDefault()
            console.log('getting download id', id)
            const uri = await getDownloadableLinkAndDownloadResource(id)
            console.log('downloadbale link', uri)
            target.setAttribute('download', '')
            target.setAttribute('href', uri)
            target.click()
        }
    }
}
