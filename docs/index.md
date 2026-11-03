# Modsmith command line

```{raw} html
<div class="hero">
  <picture>
    <source media="(max-width: 560px)" srcset="_static/hero-cli-small.svg">
    <img src="_static/hero-cli.svg" alt="">
  </picture>
  <div class="hero-copy">
    <h2>Modpacks from your terminal</h2>
    <p>Modsmith's command line finds, installs and updates modpacks, mods, resource packs and shaders from Modrinth and CurseForge, and adds them to the official Minecraft launcher.</p>
    <div class="actions">
      <a class="button primary" href="#install">Install it</a>
      <a class="button" href="get-started/quickstart/">Quick start</a>
    </div>
  </div>
</div>

<div class="band" id="install">
  <div class="band-inner single">
    <p class="eyebrow">1 · Install</p>
    <h2>Two commands, and you are set</h2>
    <p class="lede-left">uv brings the Python that Modsmith needs, so there is nothing else to install first.</p>
    <div class="tabs install" data-tabs>
      <div class="tab-list" role="tablist">
        <button type="button" role="tab" data-tab="windows">Windows</button>
        <button type="button" role="tab" data-tab="macos">macOS</button>
        <button type="button" role="tab" data-tab="linux">Linux</button>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="windows">
        <ol class="install-steps">
          <li><p><strong>Install uv.</strong> In PowerShell:</p>
            <div class="highlight-powershell notranslate"><div class="highlight"><pre>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new PowerShell window:</p>
            <div class="highlight-powershell notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="macos" hidden>
        <ol class="install-steps">
          <li><p><strong>Install uv.</strong> In Terminal:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>curl -LsSf https://astral.sh/uv/install.sh | sh</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new Terminal window:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="linux" hidden>
        <ol class="install-steps">
          <li><p><strong>Install uv:</strong></p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>curl -LsSf https://astral.sh/uv/install.sh | sh</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new terminal:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
    </div>
    <p class="install-more">Upgrading, Tab completion and other ways to install are in the <a href="get-started/installation/">installation guide</a>.</p>
  </div>
</div>

<div class="band alternate">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">2 · Find</p>
      <h2>Search both platforms at once</h2>
      <p>Look for a modpack on Modrinth and CurseForge together. Each result shows the name to give the next command.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith searching Modrinth and CurseForge">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre><span class="step" data-command='modsmith search "fabulously optimized" --type modpack --platform all'><span class="prompt">$ </span><span class="typed"></span>
<span class="out"><strong>Modrinth</strong>
<span class="dim">Name                          Use as                             Downloads</span>
Fabulously Optimized          <b class="add">modrinth:fabulously-optimized</b>          19.8M
Fabulously Optimized for PVP  <b class="add">modrinth:fabulously-optimized-pvp</b>        544
<span class="dim">Showing 2 of 73.</span>
<strong>CurseForge</strong>
<span class="dim">Name                  Use as                           Downloads</span>
Fabulously Optimized  <b class="add">curseforge:fabulously-optimized</b>       8.1M
NeoScaled             <b class="add">curseforge:neoscaled</b>                   730
<span class="dim">Showing 2 of 26.</span></span></span></pre>
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner showcase">
    <div class="band-copy">
      <p class="eyebrow">3 · Play</p>
      <h2>From a name to a game</h2>
      <ol class="steps">
        <li><strong>Install the pack</strong> Modsmith shows what it will add, and asks. Then it installs Minecraft, the mod loader and the pack's files.</li>
        <li><strong>Open the launcher</strong> The pack has its own installation, with its name and icon.</li>
        <li><strong>Play</strong> Choose it and press Play. Your other installations stay as they were.</li>
      </ol>
    </div>
    <div class="showcase-media">
      <div class="terminal" id="install-demo" data-terminal aria-label="Modsmith installing a modpack">
        <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre><span class="step" data-command="modsmith install fabulously-optimized --name survival"><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Install Fabulously Optimized 14.1.2 as survival
  <b class="add">+</b> mods/BetterGrassify-1.8.7+fabric.26.2.jar
  <b class="add">+</b> mods/cloth-config-26.2.155.jar
  <b class="add">+</b> and 100 more
<strong>102 to add; 45.0 MB to download.</strong>
Minecraft 26.2 with Fabric 0.20.1, and an installation in the official
launcher.
Install it? [Y/n]: y
Installed Fabulously Optimized as survival. In the official launcher,
choose the Fabulously Optimized installation and play.</span></span></pre>
      </div>
      <div class="launcher-demo" data-follows="install-demo" aria-label="The new installation in the official launcher">
        <div class="launcher-side"><i></i><i></i><i></i><i></i></div>
        <div class="launcher-main">
          <div class="launcher-banner"></div>
          <ul class="choices">
            <li class="choice new"><i class="icon-pack"></i><b>Fabulously Optimized<em>New</em></b><small>fabric-loader-0.20.1-26.2</small></li>
            <li class="choice"><i class="icon-grass"></i><b>Latest release</b><small>26.3</small></li>
            <li class="choice"><i class="icon-dirt"></i><b>Latest snapshot</b><small>26.4-snapshot-7</small></li>
          </ul>
          <div class="launcher-bar">
            <div class="picker"><span class="default"><i class="icon-grass"></i><b>Latest release</b><small>26.3</small></span><span class="chosen"><i class="icon-pack"></i><b>Fabulously Optimized</b><small>fabric-loader-0.20.1-26.2</small></span></div>
            <span class="launcher-play">Play</span>
            <p class="launcher-status" data-status></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="band alternate flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">4 · Make it yours</p>
      <h2>The mods they need come and go with them</h2>
      <p>Add a mod, and the mods it needs come along. Remove it, and they go again, unless something else still needs them.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith adding a mod with its dependency, then removing both">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre><span class="step" data-command="modsmith add survival jei"><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Add to survival
  <b class="add">+</b> mods/mezz_config-26.2-fabric-0.6.10.jar
  <b class="add">+</b> mods/jei-26.2-fabric-30.42.0.236.jar
    <span class="dim">MezzConfig comes too, because a mod needs it</span>
<strong>2 to add; 2.8 MB to download.</strong>
Add them? [Y/n]: y
Added to survival.</span>
</span><span class="step" data-command="modsmith remove survival jei"><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Remove from survival
  <b class="remove">-</b> mods/mezz_config-26.2-fabric-0.6.10.jar
  <b class="remove">-</b> mods/jei-26.2-fabric-30.42.0.236.jar
<strong>2 to remove.</strong>
Remove them? [Y/n]: y
Removed from survival.</span></span></pre>
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">5 · Keep it up to date</p>
      <h2>Updates that keep your changes</h2>
      <p>See what changed in the new release, and every file it touches. A file you edited is kept, marked with <code>!</code>, and a new Minecraft version moves the launcher installation with it.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith updating a modpack and keeping an edited file">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre><span class="step" data-command="modsmith update survival"><span class="prompt">$ </span><span class="typed"></span>
<span class="out"><strong>What changed in 14.1.2 for 26.2</strong>
<span class="dim">- Updated Fabric Loader to 0.20.1</span>
Update Fabulously Optimized 13.6.0 to Fabulously Optimized 14.1.2
  <b class="add">+</b> mods/BetterGrassify-1.8.7+fabric.26.2.jar
  <b class="add">+</b> and 43 more
  <b class="change">~</b> config/isxander-main-menu-credits.json
  <b class="change">~</b> and 17 more
  <b class="remove">-</b> mods/BetterGrassify-1.8.7+fabric.26.1.2.jar
  <b class="remove">-</b> and 41 more
  <b class="keep">!</b> config/modpack_defaults/options.txt
<strong>44 to add, 18 to update, 42 to remove, 1 of your changes kept; 35.8 MB to
download.</strong>
It moves from Minecraft 26.1.2 with Fabric 0.19.5 to Minecraft 26.2 with
Fabric 0.20.1.
Update them? [Y/n]: y
Updated survival.</span></span></pre>
    </div>
  </div>
</div>

<div class="band alternate flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">6 · Bring your own</p>
      <h2>Take over what you made</h2>
      <p>Already set up an installation in the launcher by hand? Import it, and Modsmith recognises its mods, so they update like the rest.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith importing an installation">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre><span class="step" data-command='modsmith import "My Fabric world"'><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Import My Fabric world as my-fabric-world: Minecraft 26.2 with Fabric
0.20.1, in D:\Games\my-fabric-world.
Import it? [Y/n]: y
  Sodium: mods/sodium-fabric-0.9.2+mc26.2.jar
  Sodium Extra: mods/sodium-extra-fabric-0.9.5+mc26.2.jar
  Entity Culling: mods/entityculling-fabric-1.11.3-mc26.2.jar
3 files can now be updated and removed like added ones.
my-fabric-world is now an instance.</span></span></pre>
    </div>
  </div>
</div>

<div class="band center">
  <div class="band-inner">
    <p class="eyebrow">Works with</p>
    <h2>Every major mod loader</h2>
    <p class="lede">Modsmith installs the loader a pack needs, or the version you choose.</p>
    <div class="loaders">
      <div class="loader"><strong>Forge</strong><span>1.13.2 and later</span></div>
      <div class="loader"><strong>NeoForge</strong><span>1.20.1 and later</span></div>
      <div class="loader"><strong>Fabric</strong><span>1.14 and later</span></div>
      <div class="loader"><strong>Quilt</strong><span>1.14.4 and later</span></div>
    </div>
  </div>
</div>

<div class="band alternate">
  <div class="band-inner single">
    <p class="eyebrow">Learn more</p>
    <h2>Where to go next</h2>
    <div class="task-groups">
      <div>
        <h3>Get started</h3>
        <a href="get-started/installation/">Installation</a>
        <a href="get-started/quickstart/">Quick start</a>
        <a href="concepts/">How Modsmith works</a>
      </div>
      <div>
        <h3>Guides</h3>
        <a href="guides/modpacks/">Install modpacks</a>
        <a href="guides/mods/">Add mods, resource packs and shaders</a>
        <a href="guides/curseforge/">Use CurseForge</a>
      </div>
      <div>
        <h3>Reference</h3>
        <a href="reference/commands/">Every command</a>
        <a href="reference/settings/">Settings</a>
        <a href="help/troubleshooting/">Troubleshooting</a>
      </div>
    </div>
  </div>
</div>

<div class="band center closing">
  <div class="band-inner">
    <h2>Building your own tool?</h2>
    <p class="lede">Everything the command line does comes from Modsmith's Python library.</p>
    <div class="actions centered">
      <a class="button primary" href="get-started/quickstart/">Start with the command line</a>
      <a class="button" href="https://modsmithmc.org/modsmith-python/">Use the Python library</a>
    </div>
  </div>
</div>
```

```{toctree}
:hidden:
:caption: Get started

get-started/index
```

```{toctree}
:hidden:
:caption: Guides

guides/index
```

```{toctree}
:hidden:
:caption: Concepts

concepts/index
```

```{toctree}
:hidden:
:caption: Reference

reference/index
```

```{toctree}
:hidden:
:caption: Help

help/index
```
