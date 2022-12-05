from administracion.forms import ContactCreateForm, ReceiptCreateForm
from administracion.models import Contact, Receipt
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone


def create_contact():
    """
    Create a Contact instace for tests
    """
    return Contact.objects.create(
        identification_type="DNI",
        identification_number="30123456",
        name="Test Case",
        situacion_iva="RM",
        address="Street test case 50",
        phone_number="3541522333",
    )


def create_receipt():
    """
    Create a Receipt instace for tests
    """
    return Receipt.objects.create(
        contact=Contact.objects.get(name="Test Case"),
        tipo="FC",
        number="A11",
        issue_date=timezone.now(),
        due_date=timezone.now(),
        detail="detalle",
        neto="100",
        iva="21",
        cai="123456789",
    )


class ContactModelTests(TestCase):
    def setUp(self):
        create_contact()

    def test_contact_creation(self):
        """
        Test if created contact is an instance of :model:`administracion.Contact`
        """
        contacto = Contact.objects.get(pk=1)
        self.assertIsInstance(contacto, Contact)

    def test_str_equals_name(self):
        """
        Test the return of "__str__" method equals to the Instance's name
        """
        contacto = Contact.objects.get(pk=1)
        self.assertEqual(contacto.__str__(), contacto.name)

    def test_validate_phone_number(self):
        """
        Test the phone number is equal to 10 numeric characters
        """
        contacto = Contact.objects.get(pk=1)
        with self.assertRaises(ValidationError, msg="Phone number is numeric"):
            contacto.phone_number = "AAAAAAAAAA"
            contacto.clean_fields()
        with self.assertRaises(ValidationError, msg="Phone number's lenght is 10"):
            contacto.phone_number = "1"
            contacto.clean_fields()

    def test_contact_uniqueness(self):
        """
        Test contact uniqueness depending on its identification type and number
        """
        contacto = Contact(
            identification_type="DNI",
            identification_number="30123456",
            name="Test Case 2",
            situacion_iva="RM",
            address="Street test case 50",
            phone_number="3541522333",
        )
        with self.assertRaises(ValidationError):
            contacto.full_clean()


class ReceiptModelTests(TestCase):
    def setUp(self):
        create_contact()
        create_receipt()

    def test_receipt_creation(self):
        """
        Test if created receipt is an instance of :model:`administracion.Receipt`
        """
        comprobante = Receipt.objects.get(pk=1)
        self.assertIsInstance(comprobante, Receipt)

    def test_validate_issue_date(self):
        """
        Test a receipt's issue date isn't in the future
        """
        comprobante = Receipt.objects.get(pk=1)
        with self.assertRaises(ValidationError, msg="Issue date is < than now"):
            comprobante.issue_date += timezone.timedelta(days=1)
            comprobante.clean_fields()

    def test_bruto(self):
        """
        Test a receipt's bruto equals to neto + iva
        """
        comprobante = Receipt.objects.get(pk=1)
        self.assertEqual(comprobante.neto + comprobante.iva, comprobante.bruto())

    def test_receipt_uniqueness(self):
        """
        Test receipt uniqueness depending on its identification type and number
        """
        comprobante = Receipt(
            contact=Contact.objects.get(name="Test Case"),
            tipo="FC",
            number="A11",
            issue_date=timezone.now(),
            due_date=timezone.now(),
            detail="detalle",
            neto="100",
            iva="21",
            cai="123456789",
        )
        with self.assertRaises(ValidationError, msg="The receipt is unique"):
            comprobante.full_clean()


class ContactFormTests(TestCase):
    def setUp(self):
        data = {
            "identification_type": "CUIT/CUIL",
            "identification_number": "12121212121212121212",
            "name": "Test Case",
            "situacion_iva": "RM",
            "address": "Street test case 50",
            "phone_number": "3541522333",
        }
        return data

    def test_valid_form(self):
        """
        Test a :form:`administracion.ContactCreateForm` is valid
        """
        data = self.setUp()
        form = ContactCreateForm(data=data)
        self.assertTrue(form.is_valid())


class ReceiptFormTests(TestCase):
    def setUp(self):
        create_contact()

    def data(self):
        return {
            "letra": "A",
            "punto_venta": "1",
            "numero": "1",
            "contact": Contact.objects.get(pk=1),
            "tipo": "FC",
            "issue_date": timezone.now(),
            "due_date": timezone.now(),
            "detail": "asd",
            "neto": 1,
            "iva": 0.5,
        }

    def test_valid_form(self):
        """
        Test a :form:`administracion.ReceiptCreateForm` is valid
        """
        data = self.data()
        # data["number"] = "A11"
        form = ReceiptCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_allowed_letter(self):
        """
        Test a form's letter is an allowed letter
        """
        data = self.data()
        data["letra"] = "S"
        form = ReceiptCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_punto_venta_isnumeric(self):
        """
        Test a form's punto_venta is an allowed character
        """
        data = self.data()
        data["punto_venta"] = "S"
        form = ReceiptCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_numero_isnumeric(self):
        """
        Test a form's numero is an allowed character
        """
        data = self.data()
        data["numero"] = "S"
        form = ReceiptCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_receipt_uniqueness(self):
        create_receipt()
        data = self.data()
        # data["numero"] = "1"
        form = ReceiptCreateForm(data=data)
        self.assertFalse(form.is_valid())


class ContactViewsTests(TestCase):
    def test_contact_list_view(self):
        """
        The empty contact's list view return an empty queryset, status_code 200 and appropiate message
        is displayed
        """
        url = reverse("contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context.get("contact_list"), [])
        self.assertContains(
            response, "No existen contactos creados. Podés crear uno haciendo click"
        )

    def test_contact_detail_view(self):
        """
        ContactDetailView returns status_code 200 and contains the contact.name,
        contact.identification_number and contact.identification_type
        """
        contact = create_contact()
        url = reverse("contact_detail", args=(contact.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            contact.name
            and contact.identification_number
            and contact.identification_type,
        )

    # def test_contact_detail_view_empty(self):
    #     """
    #     If doesnt exist :model:`administracion.Contact`'s instance, an appripiate message is displayed
    #     """
    #     url = reverse("contact_detail", args=(1))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 404)

    def test_contact_create_view(self):
        """
        ContactCreateView succesfully creates a :model:`administracion.Contact`'s instance and
        returns status_code 200
        """
        data = {
            "identification_type": "DNI",
            "identification_number": "37872924",
            "name": "Test Case",
            "situacion_iva": "RM",
            "address": "Street test case 50",
            "phone_number": "3541522333",
        }
        url = reverse("contact_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse("contact_create"), data)
        self.assertEqual(Contact.objects.get(pk=1).name, data["name"])


class ReceiptViewsTests(TestCase):
    def test_receipt_list_view(self):
        """
        The empty receipt's list view return an empty queryset, status_code 200 and appropiate message
        is displayed
        """
        url = reverse("receipt_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context.get("receipt_list"), [])
        self.assertContains(
            response, "No existen comprobantes creados. Podés crear uno haciendo click"
        )

    def test_receipt_detail_view(self):
        """
        ReceiptDetailView returns status_code 200 and contains the receipt.contact,
        receipt.tipo and receipt.number
        """
        create_contact()
        receipt = create_receipt()
        url = reverse("receipt_detail", args=(receipt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, receipt.contact and receipt.tipo and receipt.number
        )

    # def test_receipt_create_view(self):
    #     """
    #     ReceiptCreateView succesfully creates a :model:`administracion.Receipt`'s instace and
    #     returns status_code 200
    #     """
    #     create_contact()
    #     data = {
    #         "letra": "A",
    #         "punto_venta": "1",
    #         "numero": "1",
    #         "contact": Contact.objects.get(pk=1),
    #         "tipo": "FC",
    #         "issue_date": timezone.now(),
    #         "due_date": timezone.now(),
    #         "detail": "asd",
    #         "neto": 1,
    #         "iva": 0.5,
    #     }
    #     url = reverse("receipt_create")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.client.post(reverse("receipt_create"), data)
    #     self.assertEqual(Receipt.objects.get(pk=1).number, data["letra"]+data["punto_venta"]+data["numero"])
