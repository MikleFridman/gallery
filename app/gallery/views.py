import os

from PIL import Image
import moviepy.editor as moviepy
from flask import render_template, url_for, redirect, request, flash, send_file, current_app
from fpdf import FPDF

from app import db
from app.gallery import bp
from app.gallery.forms import (UploadForm, ArtworkForm, FeatureForm, FeaturesValueForm,
                               ClientForm, StatusForm, SelectTemplateForm, AttachmentForm, TagForm,
                               ArtworkTypeForm, OfferForm)
from app.gallery.models import Artwork, Attachment, Feature, Client, Status, Tag, ArtworkType, Offer


@bp.route('/')
@bp.route('/index/')
def index():
    items = Artwork.get_items()
    return render_template('index.html',
                           items=items,
                           title='Collection')


@bp.route('/features/')
def features():
    items = Feature.get_items()
    return render_template('features.html',
                           items=items,
                           title='Features')


@bp.route('/features/create/', methods=['GET', 'POST'])
def feature_create():
    form = FeatureForm()
    form.type_id.choices = ArtworkType.get_items(tuple_mode=True)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.features'))
    if form.validate_on_submit():
        feature = Feature(type_id=form.type_id.data,
                          name=form.name.data)
        db.session.add(feature)
        db.session.commit()
        return redirect(url_for('gallery.features'))
    return render_template('data_form.html',
                           title='Feature (create)',
                           form=form)


@bp.route('/features/edit/<id>', methods=['GET', 'POST'])
def feature_edit(id):
    form = FeatureForm()
    form.type_id.choices = ArtworkType.get_items(tuple_mode=True)
    feature = Feature.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.features'))
    if form.validate_on_submit():
        feature.name = form.name.data
        feature.type_id = form.type_id.data
        db.session.commit()
        return redirect(url_for('gallery.features'))
    elif request.method == 'GET':
        form.type_id.default = feature.type_id
        form.process(obj=feature)
    return render_template('data_form.html',
                           title='Feature (edit)',
                           form=form)


@bp.route('/features/delete/<id>', methods=['GET', 'POST'])
def feature_delete(id):
    feature = Feature.get_object(id)
    db.session.delete(feature)
    db.session.commit()
    return redirect(url_for('gallery.features'))


@bp.route('/features/<feature_id>/value/<artwork_id>', methods=['GET', 'POST'])
def features_value(feature_id, artwork_id):
    form = FeaturesValueForm()
    artwork = Artwork.get_object(artwork_id)
    feature = Feature.get_object(feature_id)
    form.value.label.text = feature.name
    current_value = artwork.get_feature_value(feature_id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.artwork_view', id=artwork_id))
    if form.validate_on_submit():
        if not current_value:
            artwork.add_feature_value(feature_id=feature_id,
                                      value=form.value.data)
        else:
            artwork.update_feature_value(feature_id=feature_id,
                                         value=form.value.data)
        db.session.commit()
        return redirect(url_for('gallery.artwork_view', id=artwork_id))
    elif request.method == 'GET':
        if current_value:
            form.value.data = current_value.value
    return render_template('data_form.html',
                           title='Features value (create)',
                           form=form)


@bp.route('/artworks/create/', methods=['GET', 'POST'])
def artwork_create():
    form = ArtworkForm()
    form.type_id.choices = ArtworkType.get_items(tuple_mode=True)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.index'))
    if form.validate_on_submit():
        artwork = Artwork(type_id=form.type_id.data,
                          name=form.name.data,
                          author=form.author.data,
                          year=form.year.data,
                          buy_price=form.buy_price.data,
                          info=form.info.data)
        db.session.add(artwork)
        db.session.commit()
        return redirect(url_for('gallery.index'))
    return render_template('data_form.html',
                           title='Artwork (create)',
                           form=form)


@bp.route('/artworks/view/<id>', methods=['GET', 'POST'])
def artwork_view(id):
    artwork = Artwork.get_object(id)
    data_filter = {'type_id': artwork.type_id}
    artwork_features = Feature.get_items(data_filter=data_filter)
    features_values = {f.feature_id: f.value for f in artwork.features_values}
    return render_template('artwork_view.html',
                           title='Artwork (view)',
                           item=artwork,
                           features=artwork_features,
                           values=features_values)


@bp.route('/artworks/edit/<id>', methods=['GET', 'POST'])
def artwork_edit(id):
    artwork = Artwork.get_object(id)
    form = ArtworkForm()
    form.type_id.choices = ArtworkType.get_items(tuple_mode=True)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.index'))
    if form.validate_on_submit():
        artwork.type_id = form.type_id.data
        artwork.name = form.name.data
        artwork.author = form.author.data
        artwork.year = form.year.data
        artwork.buy_price = form.buy_price.data
        artwork.info = form.info.data
        db.session.commit()
        return redirect(url_for('gallery.artwork_view', id=id))
    elif request.method == 'GET':
        form.type_id.default = artwork.type_id
        form.process(obj=artwork)
    return render_template('data_form.html',
                           title='Artwork (view)',
                           form=form)


@bp.route('/artworks/delete/<id>', methods=['GET', 'POST'])
def artwork_delete(id):
    artwork = Artwork.get_object(id)
    db.session.delete(artwork)
    db.session.commit()
    return redirect(url_for('gallery.index'))


@bp.route('/attachments/view/<id>', methods=['GET', 'POST'])
def attachment_view(id):
    attachment = Attachment.get_object(id)
    return render_template('attachment_view.html',
                           title='Attachment (view)',
                           item=attachment)


@bp.route('/attachments/edit/<id>', methods=['GET', 'POST'])
def attachment_edit(id):
    attachment = Attachment.get_object(id)
    form = AttachmentForm()
    if form.validate_on_submit():
        if form.main_image.data:
            attachment.set_main_image()
        attachment.info = form.info.data
        db.session.commit()
        return redirect(url_for('gallery.attachment_view', id=id))
    elif request.method == 'GET':
        form = AttachmentForm(obj=attachment)
    return render_template('data_form.html',
                           form=form,
                           title='Attachment (edit)')


@bp.route('/attachments/delete/<id>', methods=['GET', 'POST'])
def attachment_delete(id):
    attachment = Attachment.get_object(id)
    artwork_id = attachment.artwork.id
    attachment.delete_file()
    return redirect(url_for('gallery.artwork_view', id=artwork_id))


@bp.route('/artworks/<artwork_id>/create_pdf/', methods=['GET', 'POST'])
def create_pdf(artwork_id):
    form = SelectTemplateForm()
    artwork = Artwork.get_object(artwork_id)
    if form.validate_on_submit():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        template = form.template.data
        if template == '0':
            pdf.image(artwork.main_image.get_aws_public_url(thumbnail=True),
                      x=10, y=8, w=100)
            pdf.ln(80)
        pdf.cell(200, 10, txt="{}".format(artwork.author), ln=1)
        pdf.ln(3)
        pdf.cell(200, 10, txt="{}".format(artwork.year), ln=1)
        pdf.ln(3)
        pdf.cell(200, 10, txt="{}".format(artwork.info), ln=1)
        if template == '1':
            pdf.image(artwork.main_image.get_aws_public_url(thumbnail=True),
                      x=10, y=58, w=100)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "image.pdf")
        pdf.output(file_path, 'F')
        return send_file(file_path, as_attachment=False)
    return render_template('data_form.html', form=form)


@bp.route('/artworks/<artwork_id>/upload_file/', methods=['GET', 'POST'])
def file_upload(artwork_id):
    # bucket = s3_client.create_bucket(Bucket='11-87.tech-test',
    # CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
    url_back = url_for('gallery.artwork_view', id=artwork_id)
    artwork = Artwork.get_object(artwork_id)
    if not artwork:
        return redirect(url_back)
    form = UploadForm()
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_back)
        if 'file' not in request.files:
            flash('No selected file')
            return redirect(url_for('gallery.file_upload', artwork_id=artwork_id))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('gallery.file_upload', artwork_id=artwork_id))
        directory = os.path.join(current_app.config['UPLOAD_FOLDER'])
        if not os.path.exists(directory):
            os.mkdir(directory)
        extension = os.path.splitext(file.filename)[1]
        filename = Attachment.create_file_name(artwork, extension)
        path = os.path.join(directory, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(path)
        attachment = Attachment(artwork_id=artwork_id,
                                name=filename,
                                path=current_app.config['AWS_BUCKET_NAME'])
        db.session.add(attachment)
        db.session.flush()
        if extension not in ['.avi', '.mov', '.mp4', '.webm']:
            img = Image.open(path)
            img.thumbnail(size=(300, 500))
            path_thumb = os.path.join(directory, 'thumb_' + filename)
            img.save(path_thumb)
            attachment.aws_upload_file(path_thumb, thumbnail=True)
            attachment.aws_upload_file(path)
            if os.path.isfile(path_thumb):
                os.remove(path_thumb)
        elif not extension == '.mp4':
            clip = moviepy.VideoFileClip(path)
            path_mp4 = path.replace(extension, '.mp4')
            clip.write_videofile(path_mp4)
            attachment.name = filename.replace(extension, '.mp4')
            attachment.aws_upload_file(path_mp4)
            if os.path.isfile(path_mp4):
                os.remove(path_mp4)
        db.session.commit()
        if os.path.isfile(path):
            os.remove(path)
        return redirect(url_back)
    return render_template('data_form.html',
                           title='File upload',
                           form=form)


@bp.route('/clients/')
def clients():
    items = Client.get_items()
    return render_template('clients.html',
                           items=items,
                           title='Clients')


@bp.route('/clients/create/', methods=['GET', 'POST'])
def client_create():
    form = ClientForm()
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.clients'))
    if form.validate_on_submit():
        client = Client(name=form.name.data,
                        phone=form.phone.data,
                        birthday=form.birthday.data,
                        info=form.info.data)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('gallery.clients'))
    return render_template('data_form.html',
                           title='Client (create)',
                           form=form)


@bp.route('/clients/edit/<id>', methods=['GET', 'POST'])
def client_edit(id):
    form = ClientForm()
    client = Client.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.clients'))
    if form.validate_on_submit():
        client.name = form.name.data
        client.phone = form.phone.data
        client.birthday = form.birthday.data
        client.info = form.info.data
        db.session.commit()
        return redirect(url_for('gallery.clients'))
    elif request.method == 'GET':
        form = ClientForm(obj=client)
    return render_template('data_form.html',
                           title='Client (edit)',
                           form=form)


@bp.route('/clients/delete/<id>', methods=['GET', 'POST'])
def client_delete(id):
    client = Client.get_object(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('gallery.clients'))


@bp.route('/statuses/')
def statuses():
    items = Status.get_items()
    return render_template('statuses.html',
                           items=items,
                           title='Statuses')


@bp.route('/statuses/create/', methods=['GET', 'POST'])
def status_create():
    form = StatusForm()
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.statuses'))
    if form.validate_on_submit():
        status = Status(name=form.name.data)
        db.session.add(status)
        db.session.commit()
        return redirect(url_for('gallery.statuses'))
    return render_template('data_form.html',
                           title='Status (create)',
                           form=form)


@bp.route('/statuses/edit/<id>', methods=['GET', 'POST'])
def status_edit(id):
    form = StatusForm()
    status = Status.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.statuses'))
    if form.validate_on_submit():
        status.name = form.name.data
        db.session.commit()
        return redirect(url_for('gallery.statuses'))
    elif request.method == 'GET':
        form = StatusForm(obj=status)
    return render_template('data_form.html',
                           title='Status (edit)',
                           form=form)


@bp.route('/statuses/delete/<id>', methods=['GET', 'POST'])
def status_delete(id):
    status = Status.get_object(id)
    db.session.delete(status)
    db.session.commit()
    return redirect(url_for('gallery.statuses'))


@bp.route('/tags/')
def tags():
    items = Tag.get_items()
    return render_template('tags.html',
                           items=items,
                           title='Tags')


@bp.route('/tags/create/', methods=['GET', 'POST'])
def tag_create():
    form = TagForm()
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.tags'))
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('gallery.tags'))
    return render_template('data_form.html',
                           title='Tag (create)',
                           form=form)


@bp.route('/tags/edit/<id>', methods=['GET', 'POST'])
def tag_edit(id):
    form = TagForm()
    tag = Tag.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.tags'))
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()
        return redirect(url_for('gallery.tags'))
    elif request.method == 'GET':
        form = TagForm(obj=tag)
    return render_template('data_form.html',
                           title='Tag (edit)',
                           form=form)


@bp.route('/tags/delete/<id>', methods=['GET', 'POST'])
def tag_delete(id):
    tag = Tag.get_object(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('gallery.tags'))


@bp.route('/artwork_types/')
def artwork_types():
    items = ArtworkType.get_items()
    return render_template('artwork_types.html',
                           items=items,
                           title='Artwork types')


@bp.route('/artwork_types/create/', methods=['GET', 'POST'])
def artwork_type_create():
    form = ArtworkTypeForm()
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.artwork_types'))
    if form.validate_on_submit():
        artwork_type = ArtworkType(name=form.name.data)
        db.session.add(artwork_type)
        db.session.commit()
        return redirect(url_for('gallery.artwork_types'))
    return render_template('data_form.html',
                           title='Artwork type (create)',
                           form=form)


@bp.route('/artwork_types/edit/<id>', methods=['GET', 'POST'])
def artwork_type_edit(id):
    form = ArtworkTypeForm()
    artwork_type = ArtworkType.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.artwork_types'))
    if form.validate_on_submit():
        artwork_type.name = form.name.data
        db.session.commit()
        return redirect(url_for('gallery.artwork_types'))
    elif request.method == 'GET':
        form = ArtworkTypeForm(obj=artwork_type)
    return render_template('data_form.html',
                           title='Artwork type (edit)',
                           form=form)


@bp.route('/artwork_types/delete/<id>', methods=['GET', 'POST'])
def artwork_type_delete(id):
    artwork_type = ArtworkType.get_object(id)
    db.session.delete(artwork_type)
    db.session.commit()
    return redirect(url_for('gallery.artwork_types'))


@bp.route('/offers/')
def offers():
    items = Offer.get_items()
    return render_template('offers.html',
                           items=items,
                           title='Offers')


@bp.route('/offers/create/', methods=['GET', 'POST'])
def offer_create():
    form = OfferForm()
    form.client_id.choices = Client.get_items(tuple_mode=True)
    form.artwork_id.choices = Artwork.get_items(tuple_mode=True)
    form.status_id.choices = Status.get_items(tuple_mode=True)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.offers'))
    if form.validate_on_submit():
        offer = Offer(client_id=form.client_id.data,
                      artwork_id=form.artwork_id.data,
                      price=form.price.data,
                      info=form.info.data,
                      status_id=form.status_id.data)
        db.session.add(offer)
        db.session.commit()
        return redirect(url_for('gallery.offers'))
    return render_template('data_form.html',
                           title='Offer (create)',
                           form=form)


@bp.route('/offers/edit/<id>', methods=['GET', 'POST'])
def offer_edit(id):
    form = OfferForm()
    form.client_id.choices = Client.get_items(tuple_mode=True)
    form.artwork_id.choices = Artwork.get_items(tuple_mode=True)
    form.status_id.choices = Status.get_items(tuple_mode=True)
    offer = Offer.get_object(id)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('gallery.offers'))
    if form.validate_on_submit():
        offer.client_id = form.client_id.data
        offer.artwork_id = form.artwork_id.data
        offer.price = form.price.data
        offer.info = form.info.data
        offer.status_id = form.status_id.data
        db.session.commit()
        return redirect(url_for('gallery.offers'))
    elif request.method == 'GET':
        form.client_id.default = offer.client_id
        form.artwork_id.default = offer.artwork_id
        form.status_id.default = offer.status_id
        form.process(obj=offer)
    return render_template('data_form.html',
                           title='Offer (edit)',
                           form=form)


@bp.route('/offers/delete/<id>', methods=['GET', 'POST'])
def offer_delete(id):
    offer = Offer.get_object(id)
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('gallery.offers'))
