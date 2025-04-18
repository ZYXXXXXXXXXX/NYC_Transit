import React from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import RootComponent from './pages/RootComponent'
import { persistor, store } from './store/reducers/store'
import { BrowserRouter as Router } from 'react-router-dom'

const App: React.FC = () => {
    return (
        <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <Router>
                    <RootComponent />
                </Router>
            </PersistGate>
        </Provider>
    )
}

export default App
