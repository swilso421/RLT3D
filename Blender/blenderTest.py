#!/usr/bin/env python3.5

import SceneBuilderAPI as sbapi

sbapi.loadModel('models/THRE2068.fbx', 'THRE2068')

sbapi.renderImage('no-correction.png')

sbapi.correctLocalView()

sbapi.renderImage('with-correction.png')
