ARG DEBIAN=debian
FROM debian:${DEBIAN}
ARG PYVERSION=3

# ---
# Create the default user - vscode mounts workspace directory chowned to 1000:1000
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
&& useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
&& apt-get update \
&& apt-get install -y sudo \
&& echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
&& chmod 0440 /etc/sudoers.d/$USERNAME

# ---
# Install basic dev tools
RUN apt update \
&& apt install -y --no-install-recommends \
    ca-certificates \
    git \
    locales \
    locales-all \
    make \
&& rm -rf /var/lib/apt/lists/*

# ---
# Install python
RUN if [ $PYVERSION -eq 3 ] \
    ; then \
        apt update \
        && apt install -y --no-install-recommends \
            python3 \
            python3-distutils \
            python3-pip \
            python3-venv \
        && rm -rf /var/lib/apt/lists/* \
        && ln -s /usr/bin/python3 /usr/bin/py \
    ; else \
        echo "Install from source" \
        && apt update \
        && apt install -y --no-install-recommends \
            build-essential \
            gdb \
            lcov \
            libbz2-dev \
            libffi-dev \
            libgdbm-dev \
            libgdbm-compat-dev \
            liblzma-dev \
            libncurses5-dev \
            libreadline6-dev \
            libsqlite3-dev \
            libssl-dev \
            lzma lzma-dev \
            pkg-config \
            tk-dev \
            uuid-dev \
            zlib1g-dev \
        && rm -rf /var/lib/apt/lists/* \
        && cd /opt \
        && git clone --branch $PYVERSION --single-branch https://github.com/python/cpython \
        && cd cpython \
        && ./configure --prefix=/usr\
        && make -j \
        && make altinstall \
        && ln -s /usr/bin/python$PYVERSION /usr/bin/py \
    ; fi


# ---
# Install tools needed for building docs
RUN apt update \
&& apt install -y --no-install-recommends \
    graphviz \
    inkscape \
    latexmk \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-xetex \
    xindy \
&& rm -rf /var/lib/apt/lists/*

USER $USERNAME