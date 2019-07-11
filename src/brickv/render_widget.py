# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

render_widget.py: OpenGL OBJ Model render widget

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import os
import sys
import ctypes
import ctypes.util
import array

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat, \
                        QOpenGLShaderProgram, QOpenGLShader, \
                        QOpenGLBuffer, QVector3D, QOpenGLTexture, \
                        QImage, QMatrix4x4

from brickv.utils import get_resources_path

if sys.platform.startswith('linux'):
    libGL_path = ctypes.util.find_library('GL')
    dll_type = ctypes.CDLL
elif sys.platform.startswith('darwin'):
    libGL_path = ctypes.util.find_library('OpenGL')
    dll_type = ctypes.CDLL
else:
    libGL_path = ctypes.util.find_library('opengl32')
    dll_type = ctypes.WinDLL

libGL = dll_type(libGL_path, mode=ctypes.RTLD_GLOBAL)

GLclampf = ctypes.c_float
GLenum = ctypes.c_uint
GLsizei = ctypes.c_int
GLvoid_ptr = ctypes.c_void_p
GLbitfield = ctypes.c_uint

glClearColor = libGL.glClearColor
glClearColor.restype = None
glClearColor.argtypes = [GLclampf, GLclampf, GLclampf, GLclampf]

glEnable = libGL.glEnable
glEnable.restype = None
glEnable.argtypes = [GLenum]

glDrawElements = libGL.glDrawElements
glDrawElements.restype = None
glDrawElements.argtypes = [GLenum, GLsizei, GLenum, GLvoid_ptr]

glClear = libGL.glClear
glClear.restype = None
glClear.argtypes = [GLbitfield]

GL_DEPTH_TEST = 0x0B71
GL_CULL_FACE = 0x0B44
GL_FLOAT = 0x1406
GL_TRIANGLES = 0x0004
GL_UNSIGNED_SHORT = 0x1403
GL_UNSIGNED_INT = 0x1405


GL_DEPTH_BUFFER_BIT = 0x00000100
GL_COLOR_BUFFER_BIT = 0x00004000

class RenderWidget(QOpenGLWidget):

    def __init__(self, obj_path, parent=None):
        super().__init__(parent)

        surface_format = QSurfaceFormat()
        surface_format.setSamples(16)
        QOpenGLWidget.setFormat(self, surface_format)

        self.projection = QMatrix4x4()
        self.vertex_buf_offsets = [3, 3, 2] # position, normal, tex_coord
        self.vertex_buf_stride = sum(self.vertex_buf_offsets)

        self.obj_path = obj_path
        self.initialized = False

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if not self.initialized:
            return

        self.makeCurrent()

        self.texture.destroy()
        self.program.removeAllShaders()
        self.index_buf.destroy()
        self.vertex_buf.destroy()

        self.doneCurrent()

    def init_shaders(self):
        program = QOpenGLShaderProgram(self)
        if not program.addShaderFromSourceFile(QOpenGLShader.Vertex, get_resources_path("shader.vert")):
            return None

        if not program.addShaderFromSourceFile(QOpenGLShader.Fragment, get_resources_path("shader.frag")):
            return None

        if not program.link():
            return None

        if not program.bind():
            return None

        return program

    def init_buffers(self, vertex_positions, vertex_normals, vertex_tex_coords, faces):
        vertices = array.array('f')
        vertices_dict = {}

        indices = array.array('I')

        # We only use one index buffer, but the obj format indexes vertex positions,
        # normals and texture coordinates separately. So we create a vertex for each used
        # combination of position, normal and texture coordinate.
        for tri in faces:
            for vert_idx, tex_coord_idx, normal_idx in tri:
                key = (vert_idx, tex_coord_idx, normal_idx)

                if key in vertices_dict:
                    indices.append(vertices_dict[key])
                    continue

                vertices.extend(vertex_positions[vert_idx])
                vertices.extend(vertex_normals[normal_idx])
                vertices.extend(vertex_tex_coords[tex_coord_idx])
                assert len(vertices) % self.vertex_buf_stride == 0, 'The vertices contained data which was not aligned to the vertex_buf_stride'
                index = (len(vertices) // self.vertex_buf_stride) - 1
                vertices_dict[key] = index
                indices.append(index)

        self.bounding_sphere_radius = add_axis(self.bounding_box, vertices, indices)
        self.index_count = len(indices)

        vertex_buf = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        vertex_buf.create()
        vertex_buf.bind()
        vertex_buf.allocate(vertices, len(vertices) * vertices.itemsize)
        vertex_buf.release()

        index_buf = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        index_buf.create()
        index_buf.bind()
        index_buf.allocate(indices, len(indices) * indices.itemsize)
        index_buf.release()

        return vertex_buf, index_buf

    def initializeGL(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(4, 1)
        profile.setProfile(QSurfaceFormat.CoreProfile)

        glClearColor(0.85, 0.85, 0.85, 1.0)
        self.program = self.init_shaders()

        vertices, normals, tex_coords, faces, material = read_obj(self.obj_path)

        self.bounding_box = get_bounding_box(vertices)
        self.model_offset = -(self.bounding_box[0] + 0.5 * (self.bounding_box[1] - self.bounding_box[0])) # Offset to move the model's center into 0,0,0

        self.texture = load_texture(material)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        self.vertex_buf, self.index_buf = self.init_buffers(vertices, normals, tex_coords, faces)
        self.initialized = True

    def draw_geometry(self):
        self.vertex_buf.bind()
        self.index_buf.bind()

        offset = 0
        float_size = 4

        vertex_loc = self.program.attributeLocation("a_position")
        self.program.enableAttributeArray(vertex_loc)
        self.program.setAttributeBuffer(vertex_loc, GL_FLOAT, offset * float_size, 3, self.vertex_buf_stride * float_size)

        offset += self.vertex_buf_offsets[0]

        normal_loc = self.program.attributeLocation("a_normal")
        self.program.enableAttributeArray(normal_loc)
        self.program.setAttributeBuffer(normal_loc, GL_FLOAT, offset * float_size, 3, self.vertex_buf_stride * float_size)

        offset += self.vertex_buf_offsets[1]

        tex_coord_loc = self.program.attributeLocation("a_texcoord")
        self.program.enableAttributeArray(tex_coord_loc)
        self.program.setAttributeBuffer(tex_coord_loc, GL_FLOAT, offset * float_size, 2, self.vertex_buf_stride * float_size)

        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        self.vertex_buf.release()
        self.index_buf.release()

    def get_model_matrix(self):
        result = QMatrix4x4()
        result.translate(self.model_offset)

        return result

    def get_view_matrix(self):
        result = QMatrix4x4()
        camera_offset = 4 * self.bounding_sphere_radius
        result.translate(0.0, 0.0, -camera_offset)

        return result

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.program.bind()
        self.texture.bind()

        model = self.get_model_matrix()
        view = self.get_view_matrix()

        self.program.setUniformValue("mvp_matrix", self.projection * view * model)
        self.program.setUniformValue("model_matrix", model)
        self.program.setUniformValue("normal_matrix", model.inverted()[0].transposed())
        self.program.setUniformValue("texture", 0)
        self.program.setUniformValue("light_pos", QVector3D(self.bounding_sphere_radius * 10, self.bounding_sphere_radius * 10, self.bounding_sphere_radius * 10))
        self.program.setUniformValue("light_color", QVector3D(1, 1, 1))

        self.draw_geometry()
        self.texture.release()
        self.program.release()

    def resizeGL(self, w, h):
        aspect = float(w) / float(h if h != 0 else 1)

        scale = self.bounding_sphere_radius

        z_near = 3.0 * scale
        z_far = 5.0 * scale

        self.projection.setToIdentity()

        # Ensure that the view frustum is always greater or equal than one in width and height
        if aspect >= 1:
            self.projection.frustum(-scale * aspect, scale * aspect, -scale, scale, z_near, z_far)
        else:
            self.projection.frustum(-scale, scale, -scale / aspect, scale / aspect, z_near, z_far)


def read_mtl(mtl_file):
    with open(mtl_file, 'r') as f:
        content = f.readlines()

    current_material = None

    mtl_dir = os.path.dirname(mtl_file)

    for line in content:
        line = line.strip()

        if len(line) == 0:
            continue

        if line.startswith('newmtl '):
            if current_material is not None:
                print("Only one material is supported for now.")

            current_material = {'name': line.split(' ')[1]}
        elif line.startswith('Ka '):
            current_material['ambient'] = [float(f) for f in line.split(' ')[1:]]
        elif line.startswith('Kd '):
            current_material['diffuse'] = [float(f) for f in line.split(' ')[1:]]
        elif line.startswith('map_Ka '):
            rel_map_path = line.split(' ')[1]
            current_material['ambient_map'] = os.path.join(mtl_dir, rel_map_path)
        elif line.startswith('map_Kd '):
            rel_map_path = line.split(' ')[1]
            current_material['diffuse_map'] = os.path.join(mtl_dir, rel_map_path)

    if 'diffuse_map' in current_material and 'ambient_map' in current_material and current_material['diffuse_map'] != current_material['ambient_map']:
        print("Diffuse and ambient map are not the same texture. This is not supported.")

    return current_material

def read_obj(obj_file):
    with open(obj_file, 'r') as f:
        content = f.readlines()

    vertices = []
    normals = []
    tex_coords = []
    faces = []
    material = {}

    for line in content:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith('vn '):
            normals.append([float(f) for f in line.split(' ')[1:]])
        elif line.startswith('vt '):
            tex_coords.append([float(f) for f in line.split(' ')[1:]])
        elif line.startswith('v '):
            vertices.append([float(f) for f in line.split(' ')[1:]])
        elif line.startswith('f '):
            faces.append([[int(i) - 1 for i in x.split('/')] for x in line.split(' ')[1:]])
        elif line.startswith('mtllib '):
            obj_dir = os.path.dirname(obj_file)
            rel_mtl_path = line.split(' ')[1]
            material = read_mtl(os.path.join(obj_dir, rel_mtl_path))
        elif line.startswith('usemtl '):
            pass
        else:
            print("Could not parse line {}".format(line))
    return vertices, normals, tex_coords, faces, material

def get_bounding_box(vertices):
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0

    for x, y, z in vertices:
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        min_z = min(min_z, z)

        max_x = max(max_x, x)
        max_y = max(max_y, y)
        max_z = max(max_z, z)

    return QVector3D(min_x, min_y, min_z), QVector3D(max_x, max_y, max_z)

def add_triangle_prism(start, start_to_end, perpendicular, width, color, vertex_buf, vertex_buf_stride, index_buf):
    perpendicular = perpendicular.normalized() * width
    rotation = QMatrix4x4()
    rotation.rotate(120, start_to_end)
    index_offset = (len(vertex_buf) // vertex_buf_stride)

    vert_pos = start + perpendicular
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])
    vert_pos = vert_pos + start_to_end
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])

    vert_pos = start + rotation * perpendicular
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])
    vert_pos = vert_pos + start_to_end
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])

    vert_pos = start + rotation * rotation * perpendicular
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])
    vert_pos = vert_pos + start_to_end
    vertex_buf.extend([vert_pos.x(), vert_pos.y(), vert_pos.z(), *color, 0.0, 0.0])

    tris = [(5, 3, 2), (5, 2, 4),
            (1, 5, 4), (1, 4, 0),
            (3, 1, 0), (3, 0, 2),

            (1, 3, 5), (0, 4, 2)]

    for tri in tris:
        index_buf.extend([index_offset + i for i in tri])

def add_axis(bounding_box, vertex_buf, index_buf):
    bb_min, bb_max = bounding_box

    start = QVector3D(bb_min)
    direction = bb_max - start
    start -= 0.1 * direction

    start_to_end_x = QVector3D(bb_max.x() - start.x(), 0, 0)
    start_to_end_y = QVector3D(0, bb_max.y() - start.y(), 0)
    start_to_end_z = QVector3D(0, 0, bb_max.z() - start.z())
    max_bb_len = max(start_to_end_x.length(), start_to_end_y.length(), start_to_end_z.length())
    start_to_end_x = start_to_end_x.normalized() * max_bb_len * 0.5
    start_to_end_y = start_to_end_y.normalized() * max_bb_len * 0.5
    start_to_end_z = start_to_end_z.normalized() * max_bb_len * 0.5

    vertex_buf_stride = 3 + 3 + 2 # position, normal, tex_coord

    add_triangle_prism(start, start_to_end_x, start_to_end_y, 0.01, [1.0, 0.0, 0.0], vertex_buf, vertex_buf_stride, index_buf)
    add_triangle_prism(start, start_to_end_y, start_to_end_z, 0.01, [0.0, 0.5, 0.0], vertex_buf, vertex_buf_stride, index_buf)
    add_triangle_prism(start, start_to_end_z, start_to_end_x, 0.01, [0.0, 0.0, 1.0], vertex_buf, vertex_buf_stride, index_buf)

    return start.length()

def load_texture(material):
    # Note that the QImage is mirrored vertically to account for the fact that OpenGL and QImage use opposite directions for the y axis.
    # (https://doc.qt.io/qt-5/qopengltexture.html#details)
    texture = QOpenGLTexture(QImage(get_resources_path(material['diffuse_map'])).mirrored())
    texture.setMinificationFilter(QOpenGLTexture.Nearest)
    texture.setMagnificationFilter(QOpenGLTexture.Nearest)
    texture.setWrapMode(QOpenGLTexture.ClampToEdge)
    return texture
