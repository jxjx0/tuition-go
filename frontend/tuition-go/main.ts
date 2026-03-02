import { mountVueApp } from './vue-app/mount'

const appElement = document.getElementById('app')
if (appElement) {
    mountVueApp(appElement)
}
