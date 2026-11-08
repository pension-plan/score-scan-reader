# Public-domain hymn / chorale / chant texts, pre-syllabified with "-".
# Each entry: id, lang (eng|deu|lat), title, poet, verses (list of strings), melismatic (bool)
TEXTS = [
 dict(id="abide", lang="eng", title="Abide with Me", poet="H. F. Lyte, 1847", melismatic=False, verses=[
  "A-bide with me; fast falls the e-ven-tide; the dark-ness deep-ens; Lord, with me a-bide. When oth-er help-ers fail and com-forts flee, help of the help-less, O a-bide with me.",
  "Swift to its close ebbs out life’s lit-tle day; earth’s joys grow dim; its glo-ries pass a-way; change and de-cay in all a-round I see; O thou who chang-est not, a-bide with me.",
  "I need thy pres-ence ev-ery pass-ing hour. What but thy grace can foil the tempt-er’s power? Who, like thy-self, my guide and stay can be? Through cloud and sun-shine, Lord, a-bide with me."]),
 dict(id="ogod", lang="eng", title="O God, Our Help", poet="I. Watts, 1719", melismatic=False, verses=[
  "O God, our help in a-ges past, our hope for years to come, our shel-ter from the storm-y blast, and our e-ter-nal home.",
  "Un-der the sha-dow of thy throne thy saints have dwelt se-cure; suf-fi-cient is thine arm a-lone, and our de-fense is sure.",
  "Be-fore the hills in or-der stood, or earth re-ceived her frame, from ev-er-last-ing thou art God, to end-less years the same."]),
 dict(id="holy", lang="eng", title="Holy, Holy, Holy", poet="R. Heber, 1826", melismatic=False, verses=[
  "Ho-ly, ho-ly, ho-ly! Lord God Al-might-y! Ear-ly in the morn-ing our song shall rise to thee; ho-ly, ho-ly, ho-ly, mer-ci-ful and might-y! God in three per-sons, bless-ed Trin-i-ty!",
  "Ho-ly, ho-ly, ho-ly! All the saints a-dore thee, cast-ing down their gold-en crowns a-round the glass-y sea; cher-u-bim and ser-a-phim fall-ing down be-fore thee, which wert, and art, and ev-er-more shalt be."]),
 dict(id="amazing", lang="eng", title="Amazing Grace", poet="J. Newton, 1779", melismatic=True, verses=[
  "A-maz-ing grace! how sweet the sound that saved a wretch like me! I once was lost, but now am found, was blind, but now I see.",
  "’Twas grace that taught my heart to fear, and grace my fears re-lieved; how pre-cious did that grace ap-pear the hour I first be-lieved!",
  "Through man-y dan-gers, toils, and snares, I have al-read-y come; ’tis grace hath brought me safe thus far, and grace will lead me home."]),
 dict(id="angels", lang="eng", title="Angels We Have Heard on High", poet="Trad. French, tr. J. Chadwick", melismatic=True, verses=[
  "An-gels we have heard on high sweet-ly sing-ing o’er the plains, and the moun-tains in re-ply ech-o-ing their joy-ous strains. Glo-ri-a in ex-cel-sis De-o.",
  "Shep-herds, why this ju-bi-lee? Why your joy-ous strains pro-long? What the glad-some tid-ings be which in-spire your heav-enly song? Glo-ri-a in ex-cel-sis De-o.",
  "Come to Beth-le-hem and see him whose birth the an-gels sing; come, a-dore on bend-ed knee Christ the Lord, the new-born King. Glo-ri-a in ex-cel-sis De-o."]),
 dict(id="nundanket", lang="deu", title="Nun danket alle Gott", poet="M. Rinkart, 1636", melismatic=False, verses=[
  "Nun dan-ket al-le Gott mit Her-zen, Mund und Hän-den, der gro-ße Din-ge tut an uns und al-len En-den, der uns von Mut-ter-leib und Kin-des-bei-nen an un-zäh-lig viel zu gut bis hier-her hat ge-tan.",
  "Der e-wig-rei-che Gott woll uns bei un-serm Le-ben ein im-mer fröh-lich Herz und ed-len Frie-den ge-ben, und uns in sei-ner Gnad er-hal-ten fort und fort, und uns aus al-ler Not er-lö-sen hier und dort.",
  "Lob, Ehr und Preis sei Gott, dem Va-ter und dem Soh-ne und Gott, dem Heil-gen Geist im ho-hen Him-mels-thro-ne, ihm, dem drei-ei-nen Gott, wie es im An-fang war und ist und blei-ben wird so jetzt und im-mer-dar."]),
 dict(id="festeburg", lang="deu", title="Ein feste Burg ist unser Gott", poet="M. Luther, 1529", melismatic=False, verses=[
  "Ein fes-te Burg ist un-ser Gott, ein gu-te Wehr und Waf-fen. Er hilft uns frei aus al-ler Not, die uns jetzt hat be-trof-fen. Der alt bö-se Feind mit Ernst er’s jetzt meint; groß Macht und viel List sein grau-sam Rüs-tung ist, auf Erd ist nicht seins-glei-chen.",
  "Mit uns-rer Macht ist nichts ge-tan, wir sind gar bald ver-lo-ren; es streit’ für uns der rech-te Mann, den Gott hat selbst er-ko-ren. Fragst du, wer der ist? Er heißt Je-sus Christ, der Herr Ze-ba-oth, und ist kein an-drer Gott, das Feld muss er be-hal-ten."]),
 dict(id="wernur", lang="deu", title="Wer nur den lieben Gott läßt walten", poet="G. Neumark, 1657", melismatic=True, verses=[
  "Wer nur den lie-ben Gott lässt wal-ten und hof-fet auf ihn al-le-zeit, den wird er wun-der-bar er-hal-ten in al-ler Not und Trau-rig-keit. Wer Gott, dem Al-ler-höchs-ten, traut, der hat auf kei-nen Sand ge-baut.",
  "Was hel-fen uns die schwe-ren Sor-gen, was hilft uns un-ser Weh und Ach? Was hilft es, dass wir al-le Mor-gen be-seuf-zen un-ser Un-ge-mach? Wir ma-chen un-ser Kreuz und Leid nur grö-ßer durch die Trau-rig-keit.",
  "Man hal-te nur ein we-nig stil-le und sei doch in sich selbst ver-gnügt, wie un-sers Got-tes Gna-den-wil-le, wie sein All-wis-sen-heit es fügt; Gott, der uns sich hat aus-er-wählt, der weiß auch sehr wohl, was uns fehlt."]),
 dict(id="lobe", lang="deu", title="Lobe den Herren", poet="J. Neander, 1680", melismatic=False, verses=[
  "Lo-be den Her-ren, den mäch-ti-gen Kö-nig der Eh-ren, mei-ne ge-lieb-te See-le, das ist mein Be-geh-ren. Kom-met zu-hauf, Psal-ter und Har-fe, wacht auf, las-set den Lob-ge-sang hö-ren!",
  "Lo-be den Her-ren, der al-les so herr-lich re-gie-ret, der dich auf Ad-le-res Fit-ti-chen si-cher ge-füh-ret, der dich er-hält, wie es dir sel-ber ge-fällt; hast du nicht die-ses ver-spü-ret?"]),
 dict(id="pange", lang="lat", title="Pange lingua", poet="Thomas Aquinas", melismatic=True, verses=[
  "Pan-ge, lin-gua, glo-ri-o-si cor-po-ris mys-te-ri-um, san-gui-nis-que pre-ti-o-si, quem in mun-di pre-ti-um fruc-tus ven-tris ge-ne-ro-si rex ef-fu-dit gen-ti-um.",
  "No-bis da-tus, no-bis na-tus ex in-tac-ta Vir-gi-ne, et in mun-do con-ver-sa-tus, spar-so ver-bi se-mi-ne, su-i mo-ras in-co-la-tus mi-ro clau-sit or-di-ne.",
  "In su-pre-mae noc-te coe-nae re-cum-bens cum fra-tri-bus, ob-ser-va-ta le-ge ple-ne ci-bis in le-ga-li-bus, ci-bum tur-bae du-o-de-nae se dat su-is ma-ni-bus."]),
 dict(id="veni", lang="lat", title="Veni Creator Spiritus", poet="Rabanus Maurus", melismatic=False, verses=[
  "Ve-ni, cre-a-tor Spi-ri-tus, men-tes tu-o-rum vi-si-ta, im-ple su-per-na gra-ti-a, quae tu cre-a-sti pec-to-ra.",
  "Qui di-ce-ris Pa-ra-cli-tus, al-tis-si-mi do-num De-i, fons vi-vus, ig-nis, ca-ri-tas, et spi-ri-ta-lis unc-ti-o.",
  "Tu sep-ti-for-mis mu-ne-re, di-gi-tus pa-ter-nae dex-te-rae, tu ri-te pro-mis-sum Pa-tris, ser-mo-ne di-tans gut-tu-ra."]),
 dict(id="stabat", lang="lat", title="Stabat Mater", poet="Jacopone da Todi (attr.)", melismatic=False, verses=[
  "Sta-bat ma-ter do-lo-ro-sa jux-ta cru-cem la-cri-mo-sa, dum pen-de-bat Fi-li-us. Cu-jus a-ni-mam ge-men-tem, con-tri-sta-tam et do-len-tem per-tran-si-vit gla-di-us.",
  "O quam tri-stis et af-flic-ta fu-it il-la be-ne-dic-ta ma-ter U-ni-ge-ni-ti! Quae mae-re-bat et do-le-bat, pi-a Ma-ter, dum vi-de-bat na-ti poe-nas in-cli-ti.",
  "Quis est ho-mo qui non fle-ret, ma-trem Chri-sti si vi-de-ret in tan-to sup-pli-ci-o? Quis non pos-set con-tri-sta-ri, Chri-sti Ma-trem con-tem-pla-ri do-len-tem cum Fi-li-o?"]),
 dict(id="adeste", lang="lat", title="Adeste fideles", poet="J. F. Wade (attr.)", melismatic=True, verses=[
  "A-des-te fi-de-les, lae-ti tri-um-phan-tes, ve-ni-te, ve-ni-te in Beth-le-hem. Na-tum vi-de-te Re-gem an-ge-lo-rum: ve-ni-te a-do-re-mus, ve-ni-te a-do-re-mus Do-mi-num.",
  "Can-tet nunc i-o cho-rus an-ge-lo-rum, can-tet nunc au-la cae-le-sti-um: Glo-ri-a, glo-ri-a in ex-cel-sis De-o: ve-ni-te a-do-re-mus, ve-ni-te a-do-re-mus Do-mi-num."]),
 dict(id="aveverum", lang="lat", title="Ave verum corpus", poet="14th c.", melismatic=True, verses=[
  "A-ve, a-ve ve-rum cor-pus, na-tum de Ma-ri-a vir-gi-ne, ve-re pas-sum im-mo-la-tum in cru-ce pro ho-mi-ne, cu-jus la-tus per-fo-ra-tum un-da flu-xit et san-gui-ne, es-to no-bis prae-gus-ta-tum in mor-tis ex-a-mi-ne."]),
]
