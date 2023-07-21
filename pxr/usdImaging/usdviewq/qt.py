#
# Copyright 2017 Pixar
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#
def GetPySideModule():
    """Returns name of PySide module used by usdview,
    e.g. 'PySide2' or 'PySide6'"""
    # Inspect objects imported in a UI module generated by uic to determine 
    # which PySide module they come from (e.g. PySide2.QtCore).
    # This insulates the code from assuming that the generated code will
    # import something specific.
    from . import attributeValueEditorUI
    import inspect

    for name in dir(attributeValueEditorUI):
        obj = getattr(attributeValueEditorUI, name)
        module = inspect.getmodule(obj)
        if module and module.__name__.startswith('PySide'):
            return module.__name__.split('.')[0]

    return None
        
PySideModule = GetPySideModule()
if PySideModule == 'PySide2':
    from PySide2 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PySide2.QtOpenGL import QGLWidget as QGLWidget
    from PySide2.QtOpenGL import QGLFormat as QGLFormat
    from PySide2 import QtWidgets as QtActionWidgets
    
    # Older versions still have QtGui.QStringListModel - this
    # is apparently a bug:
    #    https://bugreports.qt.io/browse/PYSIDE-614
    if not hasattr(QtCore, 'QStringListModel'):
        QtCore.QStringListModel = QtGui.QStringListModel

    def isContextInitialised(self):
        return self.context().initialized()
    
    QGLWidget.isContextInitialised = isContextInitialised

    def bindTexture(self, qimage):
        from OpenGL import GL
        tex = self.bindTexture(qimage, GL.GL_TEXTURE_2D, GL.GL_RGBA,
                               QtOpenGL.QGLContext.NoBindOption)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex)

        return tex

    def releaseTexture(self, tex):
        from OpenGL import GL
        GL.glDeleteTextures(tex)

    QGLWidget.BindTexture = bindTexture
    QGLWidget.ReleaseTexture = releaseTexture

    def initQGLWidget(self, glFormat, parent):
        QGLWidget.__init__(self, glFormat, parent)

    QGLWidget.InitQGLWidget = initQGLWidget

elif PySideModule == 'PySide6':
    from PySide6 import QtCore, QtGui, QtWidgets, QtOpenGL
    from PySide6.QtOpenGLWidgets import QOpenGLWidget as QGLWidget
    from PySide6.QtGui import QSurfaceFormat as QGLFormat
    from PySide6 import QtGui as QtActionWidgets

    if not hasattr(QtCore.Qt, 'MatchRegExp'):
        QtCore.Qt.MatchRegExp = QtCore.Qt.MatchRegularExpression

    def isContextInitialised(self):
        return True

    QGLWidget.isContextInitialised = isContextInitialised

    QGLWidget.updateGL = QGLWidget.update

    if not hasattr(QGLWidget, 'grabFrameBuffer'):
        QGLWidget.grabFrameBuffer = QGLWidget.grabFramebuffer

    def bindTexture(self, qimage):
        tex = QtOpenGL.QOpenGLTexture(qimage)
        tex.bind()
        return tex

    def releaseTexture(self, tex):
        tex.release()
        tex.destroy()

    QGLWidget.BindTexture = bindTexture
    QGLWidget.ReleaseTexture = releaseTexture

    if not hasattr(QGLFormat, 'setSampleBuffers'):
        QGLFormat.setSampleBuffers = lambda self, _: None

    def initQGLWidget(self, glFormat, parent):
        QGLWidget.__init__(self)
        self.setFormat(glFormat)

    QGLWidget.InitQGLWidget = initQGLWidget

else:
    raise ImportError('Unrecognized PySide module "{}"'.format(PySideModule))