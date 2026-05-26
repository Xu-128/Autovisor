[33mcommit 7522430a008f38cf5bebee37359a2d95793e787b[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mauto-handle[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m, [m[1;32mmain[m[33m)[m
Author: PCX <2654559534@qq.com>
Date:   Sun May 10 21:02:37 2026 +0800

    Fix timer issue during security verification
    
    修复了限时功能在安全验证期间未暂停计时的问题.

[33mcommit 9c8ccefb6e62611bd1252e2eef169c2cc1e5f9d4[m
Author: PCX <2654559534@qq.com>
Date:   Sun May 10 20:21:51 2026 +0800

    Update README.md

[33mcommit 4cabc064b0c95fb416758d35bd22cfc38ec39558[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun May 10 20:19:04 2026 +0800

    修复计时问题

[33mcommit 9ef9e17f313fadd142452abeb81627c6391bf9f8[m
Author: PCX <2654559534@qq.com>
Date:   Fri May 8 22:53:24 2026 +0800

    Update README with logo and stability improvements
    
    Added a logo and made various optimizations for stability.

[33mcommit 0e066c69287e9a9877372666f73be22648e8a072[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri May 8 16:01:55 2026 +0800

    修复稳定性问题,优化日志模块

[33mcommit 8c69aacfdb2b4ed92ec34d18e3554155ad65d515[m
Merge: f9d6d14 832917b
Author: PCX <2654559534@qq.com>
Date:   Wed Feb 18 20:13:30 2026 +0800

    Merge pull request #132 from Disaster-Terminator/fix/config-parsing-robustness
    
    fix: 修复配置解析和进度显示的类型错误

[33mcommit 832917b3c55ea9b56c2509e3a9e078f40234147a[m
Author: Disaster-Terminator <2557058999@qq.com>
Date:   Tue Feb 17 09:33:24 2026 +0800

    fix: 限制 percent 范围为 [0, 100] 防止进度条溢出

[33mcommit b027db51548ee8bedce2fa7226a74826e8081027[m
Author: Disaster-Terminator <2557058999@qq.com>
Date:   Fri May 2 23:33:24 2025 +0800

    fix: 修复配置解析和进度显示的类型错误
    
    - 新增 _safe_get_float() 方法安全解析浮点数配置项
    - 修复 limitMaxTime/limitSpeed 为空字符串时的 ValueError (issue #107)
    - 添加默认值: limitMaxTime=0.0, limitSpeed=1.0
    - 限制 limitSpeed 有效范围为 [0.5, 1.8]
    - 修复 cur_time 为 float/None 时的 AttributeError (issue #103)
    - 添加类型检查避免对非字符串调用 .split()
    - 捕获 configparser.Error 处理缺失的 section/option

[33mcommit f9d6d14d67eac236e7bc03642c2940021752066e[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri May 2 23:33:24 2025 +0800

    3.16.4更新

[33mcommit 7de178d195cf577ca17f2243afcecba3f4498831[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri May 2 23:32:31 2025 +0800

    3.16.4更新

[33mcommit 3df4fd818ef679665e71d82ffab8bf90001d2a5a[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri May 2 23:31:24 2025 +0800

    3.16.4更新

[33mcommit 4053bd883e891831a9d962d4d2d6e0a12b6a2d55[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu Apr 3 19:07:15 2025 +0800

    添加依赖库

[33mcommit 15eaaec384ca2c2685e83c3753d5d30cf95a46e0[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu Apr 3 18:56:12 2025 +0800

    代码调整

[33mcommit 9dad6ba8e812d27cb6b9ef313b543ca718a2a6e1[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu Apr 3 18:05:29 2025 +0800

    新增自动隐藏界面功能

[33mcommit c0b84ff76e901bfdbbf9b06092a2f8faee2c7755[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:45:35 2025 +0800

    更正昵称

[33mcommit a1116733a15a3986005111c311a97ea8c1f0471b[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:40:41 2025 +0800

    修改markdown

[33mcommit 384c40c8841893fec056c472b4a0cb289fd9bb27[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:30:41 2025 +0800

    代码微调

[33mcommit 210cb8adb84cb7fc272f8f3c812a2fae55219506[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:21:32 2025 +0800

    优化组件

[33mcommit 7d134fd6b647dda396f2ef414ebcfc9f236e6878[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:09:39 2025 +0800

    代码微调

[33mcommit 2634f1456939737afa916be87e69d174e11c7b77[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 22:00:45 2025 +0800

    代码微调

[33mcommit f541e944eac16cc06007e118485322a2be46aeef[m
Merge: d1d9464 b3df5ef
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 21:57:48 2025 +0800

    Merge branch 'main' of github.com:CXRunfree/Autovisor

[33mcommit d1d946494242bdbf7b1b863174c9933e93b8d403[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 1 21:57:40 2025 +0800

    修复页面优化时的阻塞问题

[33mcommit b3df5ef58be64a66506494d4941e34f06ae5616a[m
Merge: 2d9ed62 1972cba
Author: PCX <2654559534@qq.com>
Date:   Tue Apr 1 21:29:12 2025 +0800

    Merge pull request #87 from mc139790/main
    
    拦截刷课时的人机验证请求

[33mcommit 2d9ed6243d11226d1790f6f009667c7efb221164[m
Merge: 74e4b86 1f9a2c0
Author: PCX <2654559534@qq.com>
Date:   Tue Apr 1 20:27:05 2025 +0800

    Merge pull request #86 from PencilCore/main
    
    添加针对翻转课的兼容

[33mcommit 1f9a2c0d8f496e8f28f91a249708cfce761cc2da[m
Author: Pencil <pencilzyl@gmail.com>
Date:   Tue Apr 1 17:04:55 2025 +0800

    Update README.md

[33mcommit 1972cbaba365a3e06440844ab2a593d86fffd529[m
Author: mc139790 <mc139790@gmail.com>
Date:   Tue Apr 1 09:45:45 2025 +0800

    拦截验证码请求

[33mcommit 19f6ba835ee250a84c1ac2d0dc19a62ab05d2ce9[m
Author: mc139790 <mc139790@gmail.com>
Date:   Mon Mar 31 11:56:49 2025 +0800

    fix 无法正常打开浏览器，一直刷新，如视频 #81

[33mcommit 88a728d69e36bf4f047f47d0f2e89393cf7784f5[m
Author: PencilCore <pencilzyl@gmail.com>
Date:   Fri Mar 28 12:31:16 2025 +0800

    添加针对翻转课的兼容

[33mcommit 0dbe53cd2bcec69ab2a8e2014c8f25cc0cc151c6[m
Author: PencilCore <pencilzyl@gmail.com>
Date:   Fri Mar 28 00:27:39 2025 +0800

    添加针对翻转课的兼容

[33mcommit 74e4b862a2e5e6c3a8af71e029d4ea653dac2e5b[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Mar 9 12:44:50 2025 +0800

    优化代码逻辑,提高稳定性

[33mcommit 0eb2c3dcacb9f9ef3e27c8fc5ce0953fe1502aff[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Feb 26 18:05:08 2025 +0800

    代码优化

[33mcommit 1f368ec12cdf3b30faaddfb3ced6a7ea611e1c20[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Feb 25 14:53:38 2025 +0800

    修改说明文档

[33mcommit b3240ea3290557235370745373d737be835e2619[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Feb 25 14:49:42 2025 +0800

    修改文档

[33mcommit d72c9f07e970087d1bdcd995a87003b5f398bad8[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Feb 25 14:45:12 2025 +0800

    修改说明文档

[33mcommit abcaee707159be682379ef0a1e4d1b39a59d44a6[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Feb 25 14:35:52 2025 +0800

    修复已知问题

[33mcommit b714b3459c2c6381c81c391714f8856dd7dfe96a[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Nov 5 12:39:14 2024 +0800

    修改说明文档

[33mcommit a99d57e997d6e8e52cbacc9ba3459c6f7b9014d1[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Nov 5 12:25:18 2024 +0800

    修改网址匹配模式

[33mcommit 2b5d2b7c8d38f820138489e461d00510f0cf4ca1[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Nov 5 12:24:05 2024 +0800

    修改网址匹配模式

[33mcommit d6be3bc4573e371bfccefe90978ac80688cf58a6[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Nov 1 12:52:54 2024 +0800

    内容调整

[33mcommit f85d830037effc7c33759a4638a466832ff6e736[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Nov 1 12:43:24 2024 +0800

    修复若干稳定性bug

[33mcommit 1dc57379e2972dd44e7020773b852e73c54c30b8[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Nov 1 12:06:03 2024 +0800

    支持智慧共享课,完善日志系统

[33mcommit 4f8e51b47260baf05eb8931deaad44b5c7062855[m
Author: PCX <2654559534@qq.com>
Date:   Tue Oct 15 16:14:36 2024 +0800

    Update configs.ini

[33mcommit 792465eb6884f0acac16342e90be0a6266369a63[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Oct 13 16:24:18 2024 +0800

    添加过滑块验证和依赖库下载器

[33mcommit aaaaaec8c5c7cc298ebd0792571b32bc2cec10bf[m
Merge: 4b611f8 0162a5c
Author: PCX <2654559534@qq.com>
Date:   Sat Oct 12 15:10:13 2024 +0800

    Merge pull request #38 from Towel-Fish/iss2_Nexuzi
    
    使用opencv过登录验证,隐藏模拟浏览器特征,修改build.py

[33mcommit 0162a5cf3710ea806c0a845ba1088a5b1af34ddd[m
Author: Nexuiz <lijinyong01@outlook.com>
Date:   Sat Oct 12 09:01:49 2024 +0800

    使用opencv过登录验证,隐藏模拟浏览器特征,更改build使之能正常打包

[33mcommit 4b611f8c8c38c3c2e1eafe6753e295979969329d[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sat Oct 12 00:18:59 2024 +0800

    协程bug修复

[33mcommit b20e615de342b181e9cd7ed5d157b1738192d457[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 23:46:59 2024 +0800

    修复课程界面闪退

[33mcommit 53f9ca0b0f9aa7966b0c6b01c9cd145fd44e3955[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 23:44:26 2024 +0800

    修复课程界面闪退

[33mcommit e7576144fb9af449a5c2857cd5c64979cd6e92a2[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 12:12:41 2024 +0800

    修改说明文档

[33mcommit 8cab3194fe49760972f054b2533eeca405d72b47[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 12:10:02 2024 +0800

    修改说明文档

[33mcommit 133242f72b963bf69d1a6730e040d06cf3be7f11[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 12:07:39 2024 +0800

    修改说明文档

[33mcommit 4d1e69843527a9fbf5f51586192ddce992c0e1a4[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Sep 22 11:48:34 2024 +0800

    修复若干问题

[33mcommit c07ef56843ea924af4dfe064be21c37539d58851[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Sep 20 00:14:01 2024 +0800

    异步化重构

[33mcommit 0ad7f663df91da13fab9f44ef6a6ce050259e15a[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu May 23 13:36:30 2024 +0800

    修改README.md

[33mcommit 7fff5072a7cb615afe457fd775ba907ab743b9f6[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu May 23 13:32:46 2024 +0800

    支持重复刷课

[33mcommit 6498bb897d2b599cbff69a7684db9ad078f62df5[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue May 14 22:06:35 2024 +0800

    修复无法跳转下节课的bug

[33mcommit 2ddcf154466e01c7a23b586d04483c77e1437d9c[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sat May 11 22:47:58 2024 +0800

    增加说明

[33mcommit f1212d8a0a701bbebaf1fabd3c22681f16393e56[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sat May 11 09:31:31 2024 +0800

    调整修改时间

[33mcommit 7d752e7401bf97e38211e02b8c19b6bdd5271c0d[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sat May 11 09:26:52 2024 +0800

    功能调整优化

[33mcommit d53d7f6afdec74bee5e27658fda94fec0e8e5fcb[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed May 8 23:38:03 2024 +0800

    代码结构优化

[33mcommit e3ad27bad54d3e17a7bb35cbfb8df7247f4cd156[m
Merge: d35392f 16addf8
Author: PCX <2654559534@qq.com>
Date:   Wed May 8 21:32:21 2024 +0800

    Merge pull request #17 from bwnotfound/main
    
    优化项目结构，修复题目可能无法跳过的bug，更改configs.ini编码，添加一个打包方式，优化Config，添加类型注释

[33mcommit d35392f7c5c767f7845445b1ebc02eb80859ee8e[m
Author: PCX <2654559534@qq.com>
Date:   Wed May 8 16:34:58 2024 +0800

    Create LICENSE

[33mcommit 16addf8618ae0ba6c6513249050539450ce26095[m
Author: bwnotfound <2846131442@qq.com>
Date:   Wed May 8 13:00:41 2024 +0800

    优化项目结构，修复题目可能无法跳过的bug，更改configs.ini编码，添加一个打包方式，优化Config，添加类型注释

[33mcommit 84885ae10d85fdaa30867d3f20a7cf71ea669f7e[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Apr 28 19:39:51 2024 +0800

    ver3.12.1更新

[33mcommit 461c7d2238dcd6379d6571670fdf7b3135de72b5[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu Apr 18 14:51:03 2024 +0800

    修改README.md

[33mcommit 295bfd10d0a23c702f74dddd1f858a44251ff069[m
Author: CXRunfree <2654559534@qq.com>
Date:   Thu Apr 18 14:45:58 2024 +0800

    修复学习完成后报错的问题

[33mcommit 36fba40d9e5fd1dbf2b9289a69795b1e012fd7a6[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Apr 17 18:23:42 2024 +0800

    添加自定义配置

[33mcommit 0935ac52025bbfc2abdd3066744e8f4f90bbeccd[m
Author: PCX <2654559534@qq.com>
Date:   Wed Apr 17 17:26:22 2024 +0800

    Update README.md

[33mcommit 8e6f46a91254fa7e696db3ffcd550d883f22e1ce[m
Author: PCX <2654559534@qq.com>
Date:   Wed Apr 17 17:22:29 2024 +0800

    Update README.md

[33mcommit 5044cb27fdb516d82bd689955269b4bf6cb73491[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Apr 17 17:21:18 2024 +0800

    添加自定义配置

[33mcommit a5f7246c598a6dd840bc55246ab19130692a259e[m
Author: PCX <2654559534@qq.com>
Date:   Wed Apr 10 17:48:28 2024 +0800

    Update README.md

[33mcommit cf26794208c9d238e620ee23cabea495d1412f76[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 9 12:14:55 2024 +0800

    修改README.md

[33mcommit 1498865019cfe358a6471113f4c7a9055cccef73[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 9 12:06:57 2024 +0800

    修复路径问题

[33mcommit c51454f0be8eeaa38d20d1775a6da1ddc8d6f181[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 9 12:02:46 2024 +0800

    Update README.md

[33mcommit 34c78f6b914662fa563d19f4b9ee02fb1576aba8[m
Author: PCX <2654559534@qq.com>
Date:   Tue Apr 9 11:59:46 2024 +0800

    Update README.md

[33mcommit 3d6b997da052d24c8d806e7cf30778db44021ed7[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Apr 9 11:57:34 2024 +0800

    配置文件更新,项目模块化

[33mcommit 4f3a56f015d6b88968fc2defef373cdebe3ad947[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Mar 31 00:14:33 2024 +0800

    最高支持倍速x1.8

[33mcommit b2d9d17305855eb26e3ca26678cf28348247fc12[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Mar 31 00:12:40 2024 +0800

    最高支持倍速x1.8

[33mcommit 1eb192389dd4dec4abc87910cc3d9650addfa15a[m
Author: CXRunfree <2654559534@qq.com>
Date:   Sun Mar 31 00:10:20 2024 +0800

    倍速最高支持到x1.8

[33mcommit 6c9df307dcc2d743f312de6dbae28bbb31f76d26[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Mar 20 12:38:38 2024 +0800

    修改说明

[33mcommit 0577072f9f3dc8c2ed4bf633e40d8536320d5466[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Mar 20 12:30:45 2024 +0800

    优化稳定性

[33mcommit 1c697cdc791ace129580bb5fc9c1747a4396016d[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Mar 19 22:24:25 2024 +0800

    修复播放卡死/闪退问题

[33mcommit f1bc84203bd308b0b90678c855b16217caf95474[m
Author: CXRunfree <2654559534@qq.com>
Date:   Tue Mar 19 22:23:24 2024 +0800

    修复播放卡死/闪退问题

[33mcommit c54c2d496e3e5258922499d89b02a8ee83489ec3[m
Author: PCX <2654559534@qq.com>
Date:   Sat Mar 16 16:32:11 2024 +0800

    Update README.md

[33mcommit 4f29265300326f25a45bb140c55b1d246b635d66[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Mar 15 18:15:54 2024 +0800

    修改文档说明

[33mcommit 86861bece05b64966b55ea821ed6275ecaf03671[m
Author: CXRunfree <2654559534@qq.com>
Date:   Fri Mar 15 17:50:14 2024 +0800

    优化进度判定逻辑,添加倍速画质功能

[33mcommit ba9f865b83bb1dad5c4ec8aa71b01962b674e8db[m
Author: PCX <2654559534@qq.com>
Date:   Wed Mar 13 20:24:23 2024 +0800

    Update README.md

[33mcommit 783389d90094fec06526cf38acdf0267630bfe0f[m
Author: PengChenxu <2654559534@qq.com>
Date:   Thu Mar 7 00:02:17 2024 +0800

    修改说明文档

[33mcommit 4b01b42180008fc4eb59160b74341f10d3abf2c3[m
Author: PengChenxu <2654559534@qq.com>
Date:   Wed Mar 6 16:14:29 2024 +0800

    历史版本

[33mcommit 0a17350a8d4cfbec3990b213bb2e13e87ee30db3[m
Author: CXRunfree <2654559534@qq.com>
Date:   Wed Mar 6 16:11:28 2024 +0800

    playwright重构版

[33mcommit 979a9b8b6d8d6afe5eb2ae3784c6d2dd95661f77[m
Author: CXRunfree <2654559534@qq.com>
Date:   Mon Mar 4 22:22:11 2024 +0800

    调整页面等待时间

[33mcommit d26b21a6903dc356bd1c2d5c082ccb8bcb31a51b[m
Author: CXRunfree <2654559534@qq.com>
Date:   Mon Mar 4 22:20:48 2024 +0800

    调整页面等待时间
