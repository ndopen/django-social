# Chapter 4 构建一个**social**站点
在上一章中，您学习了如何创建**SiteMap**和**Feeds**，并为博客应用构建了**搜索引擎**。在本章中，您将了解如何开发**社交应用**，这意味着用户能够加入在线平台并通过共享内容相互交互。在接下来的几章中，我们将重点介绍如何构建图片共享平台。用户将能够为互联网上的任何图片添加书签并与他人共享。他们还将能够看到他们关注的用户在平台上的活动，并且喜欢/不喜欢他们共享的图片。

在本章中，我们将首先为用户创建一个功能，用于登录，注销，编辑其密码和重置其密码。您将学习如何为用户创建自定义配置文档，并将向您的网站添加社交身份验证。

本章将涵盖以下主题：
- 使用 Django 身份验证框架
- 创建用户注册视图
- 使用自定义配置文档模型扩展用户模型
- 使用 **Python Social Auth** 添加社交身份验证

让我们从创建新项目开始。

## 4.1 创建社交网站项目
您将创建一个社交应用进程，该应用进程将允许用户共享他们在互联网上找到的图像。您需要为此项目生成以下元素：
- 供用户注册、登录、编辑个人资料以及更改或重置密码的身份验证系统
- 一个关注系统，允许用户在网站上相互关注
- 显示共享图像并实现书签的功能，供用户从任何网站共享图像
- 一个活动流，允许用户查看他们关注的人上传的内容

本章将讨论清单上的第一点。

### 4.1.1 开始您的社交网站项目
创建项目目录结构，创建**python**虚拟环境，初始化**git**及配置`.gitignore`
```shell
mkdir -p project && cd project
```

创建python虚拟环境
```shell
python3 -m venv venv .

source venv/bin/activate
```

初始化**git**，配置`.gitignore`文件，关于python的配置预设内容可以在[GitHub官方仓库](https://github.com/github/gitignore)中查询
```shell
git init

touch .gitignore
```

使用以下命令在您的虚拟环境中安装 Django：
```shell
pip install django==4.0.*
```

运行以下命令以创建新项目：
```shell
django-admin startproject bookmarks .
```

初始项目结构已创建。使用以下命令进入项目目录并创建一个名为 account 的新应用进程：
```shell
python manage.py startapp account
```

请记住，将应用进程的名称添加到 settings.py 文档中的INSTALLED_APPS设置，将新应用进程添加到项目中。将其放在INSTALLED_APPS列表中任何其他已安装的应用进程之前：
```python
INSTALLED_APPS = [
    'account.apps.AccountConfig',
]
```
稍后您将定义 Django 身份验证模板。通过将应用进程放在“INSTALLED_APPS”设置中的第一位，可以确保默认情况下将使用身份验证模板，而不是其他应用进程中包含的任何其他身份验证模板。Django在INSTALLED_APPS设置中按应用进程出现的顺序查找模板。

运行下一个命令，将数据库与INSTALLED_APPS设置中包含的默认应用进程的模型同步：
```shell
python manage.py migrate
```

您将看到所有初始 Django 数据库迁移都已应用。接下来，您将使用 Django 身份验证框架将身份验证系统构建到项目中。

此时您的项目文件如下
+ projectroot
    - account
    - bookmarks
    - docker-compose.yml
    - .git
    - .gitignore
    - venv
    - manage.py
    - db.sqlite3


## 4.2 使用 Django 身份验证框架
Django带有一个内置的身份验证框架，可以处理用户身份验证，会话，权限和用户组。身份验证系统包括常见用户操作（如登录、注销、密码更改和密码重置）的视图。

身份验证框架位于 `django.contrib.auth` 上，并由其他 **Django** 贡献包使用。请记住，您已经在第 1 章 “构建博客应用进程”中使用了身份验证框架，为博客应用进程创建一个超级用户来访问管理站点。

当您使用 startproject 命令创建新的 Django 项目时，身份验证框架将包含在项目的默认设置中。 它由 `django.contrib.auth` 应用进程和以下两个中间件类组成，这些中间件类位于项目的中间件设置中：
- **AuthenticationMiddleware**: 使用会话将用户与请求相关联
- **SessionMiddleware**: 跨请求处理当前会话

中间件是具有在请求或响应阶段全局执行的方法的类。在本书中，您将多次使用中间件类，并将在第 14 章 “上线”中学习如何创建自定义中间件。

身份验证框架还包括以下模型：
- **User** : 具有基本字段的用户模型;此模型的主要字段是 username，password，email，first_name，last_name和is_active
- **Group** : 用于对用户进行分类的组模型
- **Permission** 用户或组执行某些操作的标志
该框架还包括默认的身份验证视图和窗体，稍后您将使用它们。

### 4.2.1 创建登录视图
我们将通过使用Django身份验证框架来允许用户登录您的网站来开始本节。您的视图应执行以下操作来登录用户：
- 获取用户使用登录表单发布的用户名和密码
- 根据数据库中存储的数据对用户进行身份验证
- 检查用户是否处于活动状态
- 将用户登录到网站并启动经过身份验证的会话

首先，您将创建一个登录表单。在帐户应用进程目录中创建新的 forms.py 文档，并向其中添加以下行：
```python
from django import forms

class LoginForm(forms.Form):
    '''User Login forms'''
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
```

此表单将用于根据数据库对用户进行身份验证。请注意，您可以使用“密码输入”小组件来呈现密码 HTML 元素。这将在 HTML 中包括 **type=“password”**，以便浏览器将其视为密码输入。

编辑帐户应用进程的 **views.py** 文档，并向其中添加以下代码：
```python
from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm
from django.contrib.auth import login, authenticate
# Create your views here.

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})
```
这就是基本登录视图的作用：当使用 GET 请求调用user_login视图时，您可以使用 form = LoginForm（） 实例化一个新的登录窗体，以将其显示在模板中。当用户通过 POST 提交表单时，您可以执行以下操作：
- 使用提交的数据实例化表单 `form = LoginForm(request.POST)`
- 检查表单是否对 `form.is_valid（）` 有效。如果它无效，则在模板中显示表单错误（例如，如果用户未填写其中一个字段）。
- 如果提交的数据有效，则使用 authenticate（） 方法根据数据库对用户进行身份验证。此方法采用请求对象、用户名和密码参数，如果用户已成功通过身份验证，则返回 User 对象，否则返回 None。如果用户尚未经过身份验证，则返回原始 HttpResponse，并显示“登录无效”消息。
- 如果用户已成功通过身份验证，则可以通过访问is_active属性来检查用户是否处于活动状态。这是Django的用户模型的一个属性。如果用户未处于活动状态，则返回显示“已禁用帐户”消息的 HttpRes响应。
- 如果用户处于活动状态，则将用户登录到网站。您可以通过调用 login（） 方法在会话中设置用户，并返回“已成功通过身份验证”消息。

> 注意身份验证和登录之间的区别：authenticate（） 检查用户凭据并返回 User 对象（如果它们正确）;login（） 设置当前会话中的用户。

现在，您需要为此视图创建 URL 模式。在帐户应用进程目录中创建一个新的 urls.py 文档，并向其中添加以下代码：
```python
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login')
]

```
编辑位于书签项目目录中的主 **urls.py** 文档，导入包含并添加帐户应用进程的 URL 模式，如下所示：
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
]
```
现在可以通过 URL 访问登录视图。是时候为此视图创建模板了。由于您没有此项目的任何模板，因此您可以从创建可由登录模板扩展的基本模板开始。在帐户应用进程目录中创建以下文档和目录：
+ templates
 - account
    - login.html
 - base.html

编辑`base.html`模板并向其添加以下代码：
```python
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock  %}</title>
    <link rel="stylesheet" href="{% static "css/base.css" %}">
</head>
<body>
    <div id="header">
        <span class="logo">Bookmarks</span>
    </div>

    <div id="content">
        {% block content %}{% endblock  %}
    </div>
</body>
</html>
```
这将是网站的**base**模板。与在上一个项目中所做的那样，在主模板中包含 CSS 样式。您可以在本章附带的代码中找到这些静态文档。将帐户应用进程的 static/ 目录从分会的源代码复制到项目中的同一位置，以便您可以使用静态文档。您可以在 https://github.com/PacktPublishing/Django-3-by-Example/tree/master/Chapter04/bookmarks/account/static

base模板定义**title**和**content**块，这些标题栏和内容块可由从中延伸出来的模板填充内容。

让我们填写登录表单的模板。打开 account/login.html 模板并向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Log-in{% endblock  %}

{% block content %}
    <h1>
        Log-in
    </h1>
    <p>
        Please, use the following form to log-in:
    </p>
    <form method="post">
        {{ form.as_p }}
        {% csrf_token %}
        <p>
            <input type="submit" value="Log-in">
        </p>
    </form>
{% endblock  %}
```
此模板包括在视图中实例化的窗体。由于您的表单将通过 POST 提交，因此您将包含 {% csrf_token %} 模板标记，用于跨站点请求伪造 （CSRF） 保护。您在第 2 章 “使用高级功能增强博客”中了解了 CSRF 保护。

数据库中还没有用户。您需要先创建超级用户，以便能够访问管理站点来管理其他用户。打开命令行并执行`python manage.py createsuperuser`。填写所需的用户名、电子邮件和密码。然后，使用 `python manage.py runserver` 器命令运行开发服务器，并在浏览器中打开 http://127.0.0.1:8000/admin/ 使用刚创建的用户的凭据访问管理站点。您将看到 Django 管理站点，包括 Django 身份验证框架的用户和组模型。

它看起来如下：
![backup  Authentication User Image]()

使用管理站点创建一个新用户，并在浏览器中打开 http://127.0.0.1:8000/account/login/。您应该会看到呈现的模板，包括登录表单：
![account Log-in Form Image]()

现在，提交表单，将其中一个字段留空。在这种情况下，您将看到表单无效并显示错误，如下所示：
![account login error image]()

请注意，某些现代浏览器会阻止您提交包含空白或错误字段的表单。这是因为浏览器根据字段类型和每个字段的限制执行表单验证。在这种情况下，将不会提交表单，浏览器将显示错误字段的错误消息。

如果您输入了不存在的用户或错误的密码，您将收到无效的登录消息。

如果输入有效的凭据，您将收到“已成功通过身份验证”消息，如下所示：
![account login successfully image]()


### 4.2.2 使用 Django 身份验证视图
Django在身份验证框架中包含几个表单和视图，您可以立即使用它们。您创建的登录视图是了解Django中用户身份验证过程的良好练习。但是，在大多数情况下，您可以使用默认的Django身份验证视图。

Django提供了以下基于类的视图来处理身份验证。 它们都位于`django.contrib.auth.views`
- **LoginView**: 处理登录表单并登录用户
- **LogoutView** 注销用户

Django提供了以下视图来处理密码更改：
- **PasswordChangeView** 处理表单以更改用户的密码
- **PasspwrdChangeDoneView** 成功更改密码后将用户重定向到的成功视图

Django还包括以下视图，使用户能够重置其密码：
- **PasswordResetView** 允许用户重置其密码。它使用令牌生成一次性链接，并将其发送到用户的电子邮件帐户。
- **PasswordResetDoneView** 告知用户已向他们发送了一封电子邮件（包括用于重置其密码的链接）。
- **PasswordResetConfirmView** 允许用户设置新密码。
- **PasswordResetCompleteView** 成功重置用户密码后，用户被重定向到的成功视图。

在使用用户帐户创建网站时，上述列表中列出的视图可以为您节省大量时间。视图使用可以重写的默认值，如要呈现的模板的位置或视图要使用的窗体。

您可以在 https://docs.djangoproject.com/en/4.0/topics/auth/default/#all 身份验证视图中获取有关内置身份验证视图的详细信息。

### 4.2.3 登录和注销视图
编辑帐户应用进程的 urls.py 文档，如下所示：
```python
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```
在上面的代码中，您注释掉了之前创建的user_login视图的 URL 模式，以使用 Django 身份验证框架的 LoginView 视图。您还可以为注销视图添加 URL 模式。

在帐户应用进程的模板目录中创建一个新目录，并将其命名为**registration**。这是 Django 身份验证视图期望您的身份验证模板的默认路径。

django.contrib.admin 模块包括一些用于管理站点的身份验证模板。您已将帐户应用进程放在INSTALLED_APPS设置的顶部，以便 Django 默认使用您的模板，而不是在其他应用进程中定义的任何身份验证模板。

在templates/registeration 目录中创建一个新文档，将其命名为**login.html**，并向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Log-in
{% endblock  %}

{% block content %}
    <h1>Log-in</h1>
    {% if form.errors %}
        <p>
            Your username and password didn't match.
            Please try again.
        </p>
    {% else %}
        <p>
            Please, use the following form to log-in:
        </p>
    {% endif %}

    <div class="login-form">
        <form action="" method="post">
            {{ form.as_p }}
            {% csrf_token %}

            <input type="hidden" name="next" value="{{ next }}">
            <p>
                <input type="submit" value="Log-in">
            </p>
        </form>
    </div>
{% endblock  %}
```
此登录模板与您之前创建的模板非常相似。默认情况下，Django 使用位于**AuthenticationForm**表单。 此表单尝试对用户进行身份验证，如果登录失败，则会引发验证错误。在这种情况下，您可以使用模板中的 {% if form.errors %} 来查找错误，以检查提供的凭据是否错误。

请注意，您添加了一个隐藏的 HTML `<input>`素来提交名为 `next` 的变量的值。当您在请求中传递下一个参数时，此变量首先由登录视图设置（例如，http://127.0.0.1:8000/account/login/?next=/account/）。

`next`参数必须是 URL。如果给出此参数，Django登录视图将在成功登录后将用户重定向到给定的URL。

现在，在注册模板目录中创建一个**logged_out.html**模板，并使其如下所示：
```python
{% extends 'base.html' %}

{% block title %}
    Log-out
{% endblock  %}

{% block content %}
    <h1>Log-out</h1>

    <p>
        You have been successfully logged out.
        You can <a href="{% url 'login' %}">log-in again</a>
    </p>
{% endblock  %}
```
这是Django在用户注销后将显示的模板。

添加用于登录和注销视图的URL和模板后，您的网站现在已准备好供用户使用Django身份验证视图登录。

现在，您将创建一个新视图，以便在用户登录其帐户时显示仪表板。打开帐户应用进程的 views.py 文档，并向其中添加以下代码：
```python
from django.contrib.auth.decorators import login_required
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})
```

使用身份验证框架的login_required修饰器修饰视图。login_required装饰器检查当前用户是否已通过身份验证。如果用户已通过身份验证，它将执行修饰视图;如果用户未经过身份验证，则会将用户重定向到登录 URL，并将最初请求的 URL 作为名为 next 的 GET 参数。

通过执行此操作，登录视图会将用户重定向到他们在成功登录后尝试访问的 URL。请记住，您为此目的以登录模板的形式添加了隐藏的输入。

您还可以定义节变量。您将使用此变量来跟踪用户正在浏览的网站部分。多个视图可能对应于同一部分。这是定义每个视图所对应的部分的简单方法。

接下来，您需要为仪表板视图创建一个模板。在**templates/account**目录中创建一个新文档，并将其命名为**dashboard.html**。让它看起来像这样：
```python
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock  %}

{% block  content%}
    <h1>Dashboard</h1>
    <p>welcome to your Dashboard</p>
{% endblock  %}
```
然后，在帐户应用进程的 urls.py 文档中添加此视图的以下 URL 模式：
```python
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

编辑项目的 settings.py 文档，并向其中添加以下代码：
```python
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
```

上述代码中定义的设置如下所示：
- **LOGIN_REDIRECT_URL** 如果请求中不存在下一个参数，则告诉 Django 在成功登录后将用户重定向到哪个 URL
- **LOGIN_URL** 用于重定向用户以登录的 URL（例如，使用login_required装饰器的视图）
- **LOGOUT_URL** 重定向用户以注销的 URL

您使用的是以前使用 path（） 函数的 name 属性定义的 URL 模式的名称。硬编码的 URL（而不是 URL 名称）也可用于这些设置。

让我们总结一下到目前为止您所做的工作：
- 您已将内置的 Django 身份验证登录和注销视图添加到您的项目中
- 您已经为这两个视图创建了自定义模板，并定义了一个简单的仪表板视图，以便在用户登录后重定向用户
- 最后，您已经将 Django 的设置配置为默认使用这些 URL

现在，您将添加指向基本模板的登录和注销链接，以将所有内容放在一起。为此，您必须确定当前用户是否已登录，以便为每种情况显示适当的链接。当前用户由身份验证中间件在 `HttpRequest` 对象中设置。您可以使用请` request.user` 访问它。您将在请求中找到 User 对象，即使该用户未经过身份验证也是如此。未经身份验证的用户在请求中设置为匿名用户的实例。检查当前用户是否经过身份验证的最佳方法是访问只读属性 `is_authenticated`。

编辑您的**base.html**模板，并使用标头 ID 修改`<div>`元素，如下所示：
```python
<div id="header">
    <span class="logo">Bookmarks</span>

    {% if request.user.is_authenticated %}
        <ul class='menu'>
            <li {% if section == 'dashboard' %} class='deshboard' {% endif %}>
                <a href="{% url 'dashboard' %}"> Dashboard</a>
            </li>
            <li {% if section == 'images' %} class='deshboard' {% endif %}>
                <a href="#"> IMAGES </a>
            </li>
            <li {% if section == 'dashboard' %} class='deshboard' {% endif %}>
                <a href="#"> PEOPLE</a>
            </li>
        </ul>
    {% endif %}

    <span class="user">
        {% if request.user.is_authenticated %}
            Hello {{ request.user.first_name }}
            <a href="{% url 'logout' %}"> Logout</a>
        {% else %}
        <a href="{% url 'login' %}">Login</a>
        {% endif %}
    </span>
</div>
```
如上述代码所示，您仅向经过身份验证的用户显示站点的菜单。您还可以检查当前部分以将选定的类属性添加到相应的`<li>`项，以便使用CSS突出显示菜单中的当前部分。显示用户的名字和用于注销的链接（如果用户已通过身份验证），或显示用于以其他方式登录的链接。

现在，在浏览器中打开 http://127.0.0.1:8000/account/login/。您应该会看到登录页面。输入有效的用户名和密码，然后单击“登录”按钮。您应看到以下输出：
![account dashborad image]()

您可以看到“我的仪表板”部分使用 CSS 突出显示，因为它具有选定的类。由于用户已通过身份验证，因此用户的名字将显示在标头的右侧。单击注销链接。您应该看到以下页面：
![logout page images]()

在上述屏幕截图的页面中，您可以看到用户已注销，因此，不再显示网站的菜单。现在，标题右侧的链接显示“登录”。

> 如果您看到 Django 管理站点的已注销页面，而不是您自己的注销页面，请检查项目的INSTALLED_APPS设置，并确保 `django.contrib.admin` 在 `account.apps.AccountConfig` 应用进程之后出现。两个模板都位于相同的相对路径中，Django模板加载进程将使用它找到的第一个模板。

### 4.2.4 更改密码视图
您还需要您的用户能够在登录到您的网站后更改其密码。您将集成Django身份验证视图以更改密码。

打开帐户应用进程的 **urls.py** 文档，并向其添加以下 URL 模式：
```python
urlpatterns = [
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
```
`PasswordChangeView`视图将处理表单以更改密码，而`PasswordChangeDoneView`视图将在用户成功更改其密码后显示一条成功消息。让我们为每个视图创建一个模板。

在帐户应用进程的*templates/registration*目录中添加一个新文档，并将其命名为**password_change_form.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Change your Password{% endblock  %}

{% block content %}
    <h1>Change Your Password</h1>
    <p>use the form below change your password</p>
    <form method="post">
        {{ form.as_p }}
        <input type="submit" value="Change">
        {% csrf_token %}
    </form>
{% endblock  %}
```
**password_change_form.html**模板包含用于更改密码的表单。

现在，在同一目录中创建另一个文档，并将其命名为**password_change_done.html** 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Password changed{% endblock  %}

{% block content %}
    <h1>Password Changed</h1>
    <p>Your Password has been successfully changed.</p>
{% endblock  %}
```
**password_change_done.html**模板仅包含用户成功更改其密码时显示的成功消息。

在浏览器中打开 http://127.0.0.1:8000/account/password_change/。 如果您尚未登录，浏览器会将您重定向到登录页面。成功通过身份验证后，您将看到以下更改密码页面
![account PasswordChangeForm Image]()

在表单中填写您的当前密码和新密码，然后单击“更改”按钮。您将看到以下成功页面：
![Account PasswordChange SuccessFully Image]()
注销并使用新密码再次登录，以验证一切是否按预期工作。

### 4.2.5 重置密码视图
将以下用于Password reset的 URL 模式添加到帐户应用进程的 **urls.py** 文档中：
```python
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```
在帐户应用进程**templates/registration/**中添加一个新文档，并将其命名为**password_reset_form.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset Your Password
{% endblock  %}

{% block content %}
    <h1>Rest Your Password</h1>
    <p>Enter your e-mail address to obtain a new password.</p>

    <form method="post">
        {{ form.as_p }}
        <input type="submit" value="Send e-mail">
        {% csrf_token %}
    </form>
{% endblock  %}
```
现在，在同一目录中创建另一个文档，并将其命名为**password_reset_email**。 嗯。向其添加以下代码：
```python
Someone asked for password reset for email {{ email }}. Follow the link below:

{{ protocol }}://{{ domain }}{% url "password_reset_confirm" uidb64=uid token=token %}

Your username, in case you've forgotten: {{ user.get_username }}
```
password_reset_email.html模板将用于呈现发送给用户以重置其密码的电子邮件。它包括由视图生成的重置令牌。

在同一目录中创建另一个文档，并将其命名为**password_reset_done.html**。 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset your password
{% endblock  %}

{% block content %}
    <h1>Reset your password</h1>
    <p>We've emailed you instructions for setting your password.</p>
    <p>If you don't receive an email, please make sure you've entered the address you registered with.</p>
{% endblock  %}
```
在同一目录中创建另一个模板，并将其命名为**password_reset_confirm.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset your Password
{% endblock  %}

{% block content %}
    <h1>Reset Your Password</h1>
    {% if validlink %}
        <p>please enter your new password wtice.</p>
        <form method="post">
            {{ form.as_p }}
            {% csrf_token %}
            <p><input type="submit" value="Change My Password"></p>
        </form>
    {% else %}
        <p>The password reset link was invalid, possibly because it has already been used. Please request a new password reset.</p>
    {% endif %}
{% endblock  %}
```
在此模板中，您可以通过检查有效链接变量来检查重置密码的链接是否有效。视图密码重置确认视图检查 URL 中提供的令牌的有效性，并将有效链接变量传递给模板。如果链接有效，则显示用户密码重置表单。 仅当用户具有有效的重置密码链接时，他们才能设置新密码。

创建另一个模板并将其命名为**password_reset_complete.html**。在其中输入以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Password reset
{% endblock  %}

{% block content %}
    <h1>Password set</h1>
    <p>Your password has been set. You can
    <a href="{% url "login" %}">log in now</a></p>
{% endblock  %}

```
最后，编辑帐户应用进程的 **registration/login.html** 模板，并在 `<form>` 元素后添加以下代码：
```python
<p><a href="{% url "password_reset"%}">Forgotten your password?</a></p>
```
现在，在浏览器中打开 http://127.0.0.1:8000/account/login/，然后单击 **Forgotten your password?**链接。您应该看到以下页面：
![LoginPage Forgotten Image]()

此时，您需要将简单邮件传输协议（SMTP）配置添加到项目的 settings.py 文档中，以便Django能够发送电子邮件。您在第 2 章 “使用高级功能增强博客”中学习了如何将电子邮件设置添加到项目中。但是，在开发过程中，您可以将Django配置为将电子邮件写入标准输出，而不是通过SMTP服务器发送。Django提供了一个电子邮件后端，用于将电子邮件写入控制台。编辑项目的 settings.py 文档，然后添加以下行：
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
`EMAIL_BACKEND`设置指示用于发送电子邮件的类。
```shell
返回浏览器，输入现有用户的电子邮件地址，然后单击“SEND E-MAIL”按钮。您应该看到以下页面：
[Reset Password done Page image]()

查看运行开发服务器的控制台。您将看到生成的电子邮件，如下所示：
```python
System check identified no issues (0 silenced).
September 19, 2022 - 14:42:24
Django version 4.0.7, using settings 'bookmarks.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
[19/Sep/2022 14:42:26] "GET /account/password_reset/ HTTP/1.1" 200 1077
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Password reset on 127.0.0.1:8000
From: webmaster@localhost
To: admin@admin.com
Date: Mon, 19 Sep 2022 14:42:39 -0000
Message-ID: <166359855906.2745.14501718873517628110@sihairong.localdomain>

Someone asked for password reset for email admin@admin.com. Follow the link below:

http://127.0.0.1:8000/account/reset/MQ/bc0673-62bfb42684ced21f101d0d6f8d459076/

Your username, in case you've forgotten: admin
```

电子邮件将使用您之前创建的**password_reset_email.html**模板呈现。重置密码的URL包括由Django动态生成的令牌。

复制 URL 并在浏览器中打开它。您应该看到以下页面：
![Reset Password Image]()

用于设置新密码的页面使用`password_reset_confirm.html`模板。填写新密码，然后单击**CHANGE MY PASSWORD**按钮。Django创建一个新的哈希密码并将其保存在数据库中。您将看到以下成功页面：
![Reset Password done Image]()

现在，您可以使用新密码重新登录您的帐户。

用于设置新密码的每个令牌只能使用一次。如果再次打开收到的链接，您将收到一条消息，指出令牌无效。

现在，您已经将 Django 身份验证框架的视图集成到您的项目中。这些视图适用于大多数情况。但是，如果需要其他行为，则可以创建自己的视图。

Django还提供了您刚刚创建的身份验证URL模式。您可以注释掉已添加到帐户应用进程的 urls.py 文档中的身份验证 URL 模式，并改为包含 `django.contrib.auth.urls`，如下所示：
```python
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]
```

您可以在  https://github.com/django/django/blob/stable/4.0.x/django/contrib/auth/urls.py 中看到身份验证 URL 模式。

## 4.3 用户注册和用户配置文档
现有用户现在可以登录、注销、更改其密码和重置其密码。现在，您需要构建一个视图以允许访问者创建用户帐户。

### 4.3.1 用户注册
让我们创建一个简单的视图，以允许用户在您的网站上注册。最初，您必须创建一个表单来让用户输入用户名，其真实姓名和密码。
编辑位于帐户应用进程目录中的 **forms.py** 文档，并向其中添加以下代码：
```python
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
```
您已经为用户模型创建了一个models form。在form中，仅包含模型的username、first_name和email字段。这些字段将根据其相应的模型字段进行验证。例如，如果用户选择已存在的用户名，则会收到验证错误，因为用户名是用 unique=True 定义的字段。

您添加了两个附加字段（password 和 password2），供用户设置并确认密码。您已经定义了一个 `clean_password2（）` 方法来检查第二个密码与第一个密码，如果密码不匹配，则不让表单验证。当您通过调用表单的 `is_valid（）` 方法验证表单时，将完成此检查。您可以为任何表单域提供`clean_<fieldname>()` 方法，以便清理值或引发特定字段的表单验证错误。表单还包括一个通用的 `clean（）` 方法来验证整个表单，这对于验证相互依赖的字段非常有用。在这种情况下，您可以使用特定于字段的 `clean_password2（）` 验证，而不是重写form的 `clean（）` 方法。这样可以避免覆盖 `ModelForm` 从模型中设置的限制中获取的其他特定于字段的检查（例如，验证用户名是否唯一）。

Django还提供了一个你可以使用的`UserCreationForm`，它驻留在`django.contrib.auth.forms`中，与你创建的表单非常相似。

编辑帐户应用进程的 **views.py** 文档，并向其中添加以下代码：
```python
from .forms import LoginForm, UserRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            return render(request, 'account/register_done.html', {'new_user': new_user})

    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'account/register.html', {'user_form': user_form})
```
创建用户帐户的视图非常简单。出于安全原因，您不是保存用户输入的原始密码，而是使用处理哈希的用户模型的 `set_password（）` 方法。

现在，编辑帐户应用进程的 **urls.py** 文档，并添加以下 URL 模式：
```python
urlpatterns = [
    path('register/', views.register, name='register'),
]
```

最后，在**account/templates**目录中创建一个新模板，将其命名为**register.html**，并使其如下所示：
```python
{% extends 'base.html' %}

{% block title %}
    Register Your Account
{% endblock  %}

{% block content %}
    <h1>Register Your Account</h1>
    <p>please sign up using the following form:</p>

    <form method="post">
        {{ user_form.as_p }}
        {% csrf_token %}
        <p>
            <input type="submit" value="Create my account">
        </p>
    </form>
{% endblock  %}
```

在同一目录中添加模板文档，并将其命名为**register_done.html**。 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Welcome
{% endblock  %}

{% block content %}
    <h1>Welcome {{ new_user.first_name }}!</h1>
    <p>Your account has been successfully created. Now you can <a href="{% url "login" %}">log in</a>.</p>
{% endblock  %}
```

现在在浏览器中打开 http://127.0.0.1:8000/account/register/。您将看到您创建的注册页面：
![Account RegisterPage image]()

填写新用户的详细信息，然后单击**CREATE MY ACCOUNT**按钮。 如果所有字段都有效，则将创建用户，并且您将收到以下成功消息：
![Account Register succees image]()

单击登录链接并输入您的用户名和密码，以验证您是否可以访问您的帐户。

您还可以在登录模板中添加注册链接。编辑 registration/login.html 模板并找到以下行：
```python
<p>Please, use the following form to log-in. If you don't have an account <a href="{% url "register" %}">register here</a></p>
```

您已使注册页面可从登录页面访问。
### 4.3.2 扩展用户模型
当您必须处理用户帐户时，您会发现Django身份验证框架的用户模型适用于常见情况。但是，用户模型附带了非常基本的字段。您可能希望扩展它以包含其他数据。执行此操作的最佳方法是创建一个配置文档模型，其中包含所有其他字段以及与 Django 用户模型的一对一关系。 一对一关系类似于参数为 unique=True 的外键字段。关系的反面是与相关模型的隐式一对一关系，而不是多个元素的管理器。 从关系的每一端，检索单个相关对象。

编辑帐户应用进程的 models.py 文档，并向其中添加以下代码：
```python
from django.conf import settings
from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/%Y/%m/%d/', blank = True)

    def __str__(self):
        return f'profile for user {self.user.username}'
```

> 为了使代码保持通用，请使用 `get_user_model（）` 方法检索用户模型，并使用AUTH_USER_MODEL设置在定义模型与用户模型的关系时引用它，而不是直接引用身份验证用户模型。有关此内容的详细信息，请参阅 https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#django.contrib.auth.get_user_model

用户一对一字段允许您将配置文档与用户相关联。将 CASCADE 用于on_delete参数，以便在删除用户时也删除其相关配置文档。照片字段是图像字段字段。您需要安装Pillow库来处理图像。通过在 shell 中运行以下命令来安装 Pillow：
```shell
pip install pillow
```

要使 Django 能够提供用户通过开发服务器上传的媒体文档，请将以下设置添加到项目的 settings.py 文档中：
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```
**MEDIA_URL**是用于提供用户上传的媒体文档的基本URL，**MEDIA_ROOT**是用户所在的本地路径。您可以相对于项目路径动态生成路径，以使代码更加通用。

现在，编辑书签项目的主 urls.py 文档并修改代码，如下所示：
```python
from django.conf import settings

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
```
这样，Django开发服务器将负责在开发期间（即当DEBUG设置设置为True时）提供媒体文档。

> static（） 帮助进程函数适用于开发，但不适用于生产用途。Django在提供静态文档方面效率非常低下。永远不要在生产环境中使用 Django 提供静态文档。您将在第 14 章 “上线”中学习如何在生产环境中提供静态文档。
打开 shell 并运行以下命令，为新模型创建数据库迁移,同步数据库：
```shell
python manage.py makemigrations
python manage.py migate
```

编辑帐户应用进程的 **admin.py** 文档，并在管理站点中注册配置文档模型，如下所示：
```python
from django.contrib import admin
from account.models import Profile

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
```

使用 python manage.py 运行服务器命令运行开发服务器，并在浏览器中打开 http://127.0.0.1:8000/admin/。现在，您应该能够在项目的管理站点中看到配置文档模型，如下所示：
![Backup Profile Edit image]()

接下来，您将允许用户在网站上编辑其个人资料。将以下导入和模型表单添加到帐户应用进程的 forms.py 文档中：
```python
from django.contrib.auth.models import User
from .models import Profile

class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')

```

这些forms如下：
    - **UserEditForm**: 这将允许用户编辑他们的**first_name**，**last_name**和**email**，这些是内置Django用户模型的属性。
    - **ProfileEditForm**: 这将允许用户编辑保存在自定义配置文档模型中的配置文档数据。用户将能够编辑他们的**birth date**并上传其个人资料的**photo**。

编辑帐户应用进程的 **views.py** 文档并导入配置文档模型，如下所示：
```python
from .forms import LoginForm, ProfileEditForm, UserEditForm, UserRegistrationForm
from .models import Profile
```
然后，将以下行添加到`new_user.save()` 下方的**register**视图中：
```python
Profile.objects.create(user = new_user)
```
当用户在您的网站上注册时，您将创建一个与他们关联的空个人资料。您应使用管理站点为之前创建的用户手动创建配置文档对象。

现在，您将允许用户编辑其个人资料。将以下代码添加到同一文档中：
```python
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form':user_form, 'profile_form':profile_form})
```
使用login_required装饰器，因为用户必须经过身份验证才能编辑其配置文档。在这种情况下，您将使用两个模型窗体：用户编辑窗体用于存储内置用户模型的数据，以及“配置文档编辑窗体”用于在自定义配置文档模型中存储其他配置文档数据。若要验证提交的数据，请执行两个窗体的 `is_valid（）` 方法。如果两个表单都包含有效数据，则保存这两个表单，并调用 `save（）` 方法来更新数据库中的相应对象。

将以下 URL 模式添加到帐户应用进程的 urls.py 文档中：
```python
path('edit/', views.edit, name='edit')
```

最后，在**templates/account/**中为此视图创建一个模板，并将其命名为**edit.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Edit your account
{% endblock  %}

{% block content %}
    <h1>Edit your account</h1>
    <p>You can edit your account using the following form:</p>

    <form method="post" enctype="multipart/form-data">
        {{user_form.as_p}}
        {{profile.as_p}}
        {% csrf_token %}
        <p><input type="submit" value="save changes"></p>
    </form>
{% endblock  %}
```

在上面的代码中，您可以在表单中包含 `enctype="multipart/form-data"`以启用文档上传。您可以使用 HTML 表单提交`user_form`和`profile_form`表单。

从 URL http://127.0.0.1:8000/account/register/ 注册新用户并打开 http://127.0.0.1:8000/account/edit/。您应该看到以下页面：
![Account Edit Page]()

您还可以编辑仪表板页面，并包括指向编辑配置文档和更改密码页面的链接。打开 account/dashboard.html 模板并找到以下行：
```python
<p>Welcome to your dashboard.</p>
```
将前面的行替换为以下行：
```python
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock  %}

{% block  content%}
    <h1>welcome to your dashboard</h1>
    <p>Welcome to your dashboard. You can <a href="{% url "edit" %}">edit your profile</a> or <a href="{% url "password_change" %}">change your password</a>.</p>
{% endblock  %}
```
用户现在可以访问表单以从其仪表板编辑其个人资料。在浏览器中打开 http://127.0.0.1:8000/account/ 并测试新链接以编辑用户的个人资料：
![dashboard pages]()

#### 4.3.2.1 使用自定义用户模型
Django还提供了一种用自己的自定义模型替换整个用户模型的方法。您的用户类应继承自 Django 的 `AbstractUser` 类，该类将默认用户的完整实现作为抽象模型提供。您可以在  https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model 自定义用户模型中阅读有关此方法的更多信息。

使用自定义用户模型将为您提供更大的灵活性，但它也可能导致与Django的身份验证用户模型交互的可插入应用进程的集成更加困难。

### 4.3.3 使用消息框架



## 4.4 构建自定义身份验证后端


## 4.5 向网站添加社交身份验证

### 4.5.1 通过 HTTPS 运行开发服务器

### 4.5.2 使用脸书进行身份验证

### 4.5.3 使用推特进行身份验证

### 4.5.4 使用谷歌进行身份验证


## 4.6 概述