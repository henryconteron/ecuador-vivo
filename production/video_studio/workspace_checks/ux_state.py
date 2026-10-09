"""Real Chrome regressions for rejected edits and background-worker reruns."""
import asyncio
import json
from ux_browser import Browser, ROOT


async def run():
    browser = await Browser().start()
    checks = []

    async def evaluate(code):
        return await browser.evaluate("const q=id=>all().find(e=>e.id===id);" + code)

    async def version():
        return int(await evaluate("return all().find(e=>e.classList.contains('evs')).dataset.version"))

    async def commit(code):
        previous = await version()
        await evaluate(code)
        await browser.wait("Number(all().find(e=>e.classList.contains('evs')).dataset.version)>" + str(previous))

    async def check(expression, label):
        assert await evaluate('return ' + expression), label
        checks.append(label)

    try:
        await browser.call('Runtime.enable')
        await browser.call('Page.navigate', {'url': 'http://127.0.0.1:8512'})
        await browser.wait("all().some(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio'))")
        await evaluate("all().find(e=>e.tagName==='BUTTON'&&e.textContent.includes('5 · Estudio')).click()")
        await browser.wait("all().some(e=>e.id==='project-menu')")
        await evaluate("q('project-menu').click()")
        await commit("[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent.includes('Nuevo proyecto')).click()")
        previous = await version()
        await evaluate("q('scene-duration').value='0';q('scene-duration').dispatchEvent(new Event('change'))")
        await browser.wait("all().some(e=>e.id==='workspace-status'&&e.getAttribute('role')==='alert')")
        await check("q('scene-duration').value==='0'", 'rejected field value survives error rerun')
        assert await version() == previous
        checks.append('rejected edit preserves accepted revision')
        await commit("q('scene-duration').value='8';q('scene-duration').dispatchEvent(new Event('change'))")
        await check("q('save-state').dataset.state==='saved'", 'corrected field saved atomically')
        await evaluate("q('format').click();const fields=q('dialog-body').querySelectorAll('input');q('dialog-body').querySelector('select').value='custom';q('dialog-body').querySelector('select').dispatchEvent(new Event('change'));fields[0].value='1280';fields[1].value='720'")
        await commit("[...q('dialog-body').querySelectorAll('button')].find(e=>e.textContent.includes('Adaptar')).click()")
        await evaluate("q('scene-duration').value='7.25';q('scene-duration').focus();q('play').click()")
        await browser.wait("all().some(e=>e.id==='save-state'&&e.dataset.state==='saved')")
        await check("q('scene-duration').value==='7.25'", 'unsubmitted field survives worker acknowledgement')
        await check("q('scene-duration').getRootNode().activeElement===q('scene-duration')", 'inspector focus survives transient rerun')
        await commit("q('project-name').value='Worker anterior conservado';q('project-name').dispatchEvent(new Event('change'))")
        await browser.wait("all().some(e=>e.id==='workspace-status'&&e.textContent.includes('El documento cambió'))")
        await evaluate("q('export').click()")
        await check("[...q('dialog-body').querySelectorAll('button')].some(e=>e.textContent==='Exportación en curso'&&e.disabled)", 'document changed while actual worker running')
        await evaluate("q('dialog-close').click()")
        # Poll only the public dialog. The component must continue polling the
        # original job even though its document is now stale.
        completed = False
        for _ in range(90):
            await asyncio.sleep(1)
            await evaluate("q('export').click()")
            completed = await evaluate("return [...q('dialog-body').querySelectorAll('button')].some(e=>e.textContent==='Exportar MP4'&&!e.disabled)")
            await evaluate("q('dialog-close').click()")
            if completed:
                break
        assert completed, 'stale worker never completed in UI'
        checks.append('stale worker completion updates public controls')
        await check("q('scene-duration').value==='8'", 'accepted revision replaces old unsubmitted draft')
        for zoom in (50, 250):
            await evaluate("q('time-zoom').value='" + str(zoom) + "';q('time-zoom').dispatchEvent(new Event('input'))")
            await check("Math.abs(q('time-ruler').lastElementChild.getBoundingClientRect().right-q('scenes').lastElementChild.getBoundingClientRect().right)<2", 'ruler matches scene end at zoom ' + str(zoom))
        assert not [e for e in browser.events if e.get('method') == 'Runtime.exceptionThrown']
        result = {'checks': checks, 'count': len(checks)}
        (ROOT / 'ux-redesign' / 'state.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    except Exception:
        await browser.shot('debug-state-failure.png')
        print('FAILED', checks, await evaluate("return q('workspace-status')?.textContent"), flush=True)
        raise
    finally:
        await browser.close()


asyncio.run(run())
