# -*- coding: utf-8 -*-
# Part of Wicoders Solutions. See LICENSE file for full copyright and licensing details

{
    'name': 'Website Video Snippet',
    'version': '19.0.0.1',
    'license': 'AGPL-3',
    'category': 'Website/Website',
    'summary': """ 
        Add local videos to your website with an intuitive drag-and-drop interface.
    """,
    'description': """
        Enhance your website by allowing users to drag and drop local video files directly onto the page using the Website Video Snippet by Wicoders Solutions. 
        Key Features:
        - Drag and drop local video files.
        - Seamless integration with the Odoo website editor.
        - Easy to customize and user-friendly.
    """,
    'depends': ['website'],
    'data': [
        'views/attachment_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'website.website_builder_assets': [
            'wi_video_snippet/static/src/xml/embed_video.xml',
            'wi_video_snippet/static/src/snippets/embed_video.js',
        ]
    },
    'images': [
        'static/description/banner.png',
    ],
    'price': 00.00,
    'currency': 'USD',
    'author': 'Wicoders Solutions',
    'website': 'https://wicoders.com',
    'maintainer': 'Wicoders Solutions',

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
