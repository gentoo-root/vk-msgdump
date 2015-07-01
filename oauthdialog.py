from PyQt4 import QtCore, QtGui, QtWebKit

class OAuthDialog(QtWebKit.QWebView):
    def __init__(self, redirect_uri=None, parent=None):
        QtWebKit.QWebView.__init__(self, parent)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.setPage(_OAuthPage(redirect_uri, self))
        self.page().authFinished.connect(self.authFinished)
        self.page().geometryChangeRequested.connect(self.webSetGeometry)
        self.titleChanged.connect(self.webSetTitle)
        self.iconChanged.connect(self.webUpdateIcon)

    def createWindow(self, win_type):
        # It's not difficult to implement, but it's not necessary as for now
        raise NotImplementedError('Creating multiple windows is not implemented')

    @QtCore.pyqtSlot('QRect')
    def webSetGeometry(self, geom):
        if not self.parent():
            self.setGeometry(geom)

    @QtCore.pyqtSlot('QString')
    def webSetTitle(self, title):
        self.setWindowTitle(title)

    @QtCore.pyqtSlot()
    def webUpdateIcon(self):
        self.setWindowIcon(self.icon())

    authFinished = QtCore.pyqtSignal('QString')

class _OAuthPage(QtWebKit.QWebPage):
    def __init__(self, redirect_uri=None, parent=None):
        QtWebKit.QWebPage.__init__(self, parent)
        self._redirect_uri = redirect_uri

    def acceptNavigationRequest(self, frame, request, nav_type):
        if frame is None: # new window should be opened
            QtGui.QDesktopServices.openUrl(request.url())
            return False

        if self._redirect_uri:
            url = bytes(request.url().toEncoded()).decode('ascii')
            if url.startswith(self._redirect_uri + '#'):
                self.authFinished.emit(url)
                return False

        return QtWebKit.QWebPage.acceptNavigationRequest(self, frame, request, nav_type)

    authFinished = QtCore.pyqtSignal('QString')
