#!/usr/bin/env python3.5

import SceneBuilderAPI as sbapi

sbapi.loadModel('models/THRE2068.fbx', 'THRE2068')

sbapi.renderImage()

sbapi.correctLocalView()

sbapi.renderImage()
